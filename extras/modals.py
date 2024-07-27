import discord

from configparser import ConfigParser

from utils import sqlmgr
from extras import embeds, views

from time import time as timenow

CONFIG = ConfigParser()
CONFIG.read("config.cfg")

MSG_CHANNEL = int(CONFIG["Form"]["msg_channel"])
SUBMIT_CHANNEL = int(CONFIG["Form"]["submit_channel"])

DATABASE = sqlmgr.DatabaseManager("data/form_data.db")


class FormModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Заявка на получение роли Steam Content Makers",
            custom_id="form_modal",
            timeout=None
        )

        self.elements = {
            "steam_profile_url": discord.ui.InputText(
                style=discord.InputTextStyle.short,
                custom_id="steam_profile_url",
                label="Ссылка на ваш профиль Steam",
                placeholder="https://steamcommunity.com/id/...",
                min_length=31,
                max_length=100,
                required=True
            ),
            "steam_content_url": discord.ui.InputText(
                style=discord.InputTextStyle.long,
                custom_id="steam_content_url",
                label="Ссылки на ваши творчества Steam",
                placeholder="https://steamcommunity.com/sharedfiles/filedetails/?id=...",
                min_length=56,
                max_length=800,
                required=True
            ),
            "claimed_roles": discord.ui.InputText(
                style=discord.InputTextStyle.long,
                custom_id="claimed_roles",
                label="Роли, на которые вы претендуете",
                placeholder="Писатель руководств\nИллюстратор\nМододел и так далее...",
                min_length=1,
                max_length=200,
                required=True
            )
        }

        for e in self.elements.values():
            self.add_item(e)

    async def callback(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True)

        uploader = inter.user
        profile_url = self.elements["steam_profile_url"].value
        content_url = self.elements["steam_content_url"].value
        claimed_roles = self.elements["claimed_roles"].value

        DATABASE.write_form_data(
            uid=uploader.id,
            upload_time=round(timenow()),
            steam_profile_url=profile_url,
            steam_content_url=content_url,
            claimed_roles=claimed_roles
        )

        form_id = DATABASE.exctract_record_data(uid=uploader.id)["id"]
        channel = inter.guild.get_channel(SUBMIT_CHANNEL)

        embed = embeds.FormSubmittedInfoEmbed(
            form_id,
            uploader,
            profile_url,
            content_url,
            claimed_roles
        )

        await channel.send(embed=embed, view=views.FormModSubmitView(uploader.id))

        response_embed = embeds.FormSubmitSuccessEmbed(form_id)

        await inter.respond(embed=response_embed, ephemeral=True)