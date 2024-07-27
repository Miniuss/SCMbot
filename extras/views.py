import discord

from configparser import ConfigParser

from utils import sqlmgr
from extras import embeds, modals

CONFIG = ConfigParser()
CONFIG.read("config.cfg")

ADMIN_ROLES = list(map(int, CONFIG["Perms"]["admin_roles"].replace(" ", "").split(",")))
NO_FORM_ROLES = list(map(int, CONFIG["Perms"]["no_form_roles"].replace(" ", "").split(",")))

DATABASE = sqlmgr.DatabaseManager("data/form_data.db")

class FormUploadView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        custom_id="form_upload_button",
        label="Написать заявку",
        emoji="📝",
        style=discord.ButtonStyle.green
    )
    async def form_upload_button(self, button: discord.ui.Button, inter: discord.Interaction):
        data = DATABASE.exctract_record_data(uid=inter.user.id)

        uploader_roles = inter.user.roles

        if data is not None:
            embed = embeds.FormAlreadySubmittedEmbed(data["id"])

            await inter.respond(embed=embed, ephemeral=True)
            return
        
        if any(role.id in NO_FORM_ROLES for role in uploader_roles):
            embed = embeds.FromSubmitterHasRoleEmbed()

            await inter.respond(embed=embed, ephemeral=True)
            return
        
        await inter.response.send_modal(modals.FormModal())

class FormModSubmitView(discord.ui.View):
    def __init__(self, uid: int):
        super().__init__(timeout=None)
        self.uid = uid

    @discord.ui.button(
        custom_id="form_approve_button",
        label="Принять форму",
        emoji="✔️",
        style=discord.ButtonStyle.green
    )
    async def approve(self, button: discord.ui.Button, inter: discord.Interaction):
        uploader = inter.guild.get_member(self.uid)
        approver = inter.user

        if not any(role.id in ADMIN_ROLES for role in approver.roles):
            response_embed = embeds.FormNoPermsEmbed()

            await inter.respond(embed=response_embed, ephemeral=True)
            return

        if uploader is None:
            DATABASE.remove_record(uid=self.uid)

            response_embed = embeds.FormOwnerNotFoundEmbed()

            await inter.respond(response_embed)
            self.disable_all_items()

            await inter.message.edit(view=self)

            return

        if DATABASE.exctract_record_data(uid=self.uid)["approver_uid"] is not None:
            response_embed = embeds.FormApprovalActionInboundEmbed()

            await inter.respond(embed=response_embed, ephemeral=True)
            return
        
        await inter.response.defer()

        DATABASE.role_approval(approver.id, uid=self.uid)

        user_embed = embeds.FormApprovedEmbed(
            inter.guild.name,
            approver
        )

        dm_channel = await uploader.create_dm()
        
        await dm_channel.send(embed=user_embed)

        response_embed = embeds.MemberApprovedFormEmbed(approver)

        self.disable_all_items()

        await inter.message.edit(view=self)
        await inter.respond(embed=response_embed)

    @discord.ui.button(
        custom_id="form_disapprove_button",
        label="Отклонить форму",
        emoji="✖️",
        style=discord.ButtonStyle.red
    )
    async def reject(self, button: discord.ui.Button, inter: discord.Interaction):
        uploader = inter.guild.get_member(self.uid)
        approver = inter.user

        if not any(role.id in ADMIN_ROLES for role in approver.roles):
            response_embed = embeds.FormNoPermsEmbed()

            await inter.respond(embed=response_embed, ephemeral=True)
            return

        if uploader is None:
            DATABASE.remove_record(uid=self.uid)

            response_embed = embeds.FormOwnerNotFoundEmbed()
            await inter.respond(response_embed)
            self.disable_all_items()

            await inter.message.edit(view=self)

            return

        if DATABASE.exctract_record_data(uid=self.uid)["approver_uid"] is not None:
            response_embed = embeds.FormApprovalActionInboundEmbed()

            await inter.respond(embed=response_embed, ephemeral=True)
            return
        
        await inter.response.defer()

        DATABASE.role_approval(approver.id, uid=self.uid)

        user_embed = embeds.FormDeniedEmbed(
            inter.guild.name,
            approver
        )

        dm_channel = await uploader.create_dm()

        await dm_channel.send(embed=user_embed)

        response_embed = embeds.MemberDeniedFormEmbed(approver)

        self.disable_all_items()

        await inter.message.edit(view=self)
        await inter.respond(embed=response_embed)