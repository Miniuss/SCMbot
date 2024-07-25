import discord
from discord.ext import commands
from utils import logs
import traceback

from cogs.forms import FormUploadView, FormModSubmitView
from utils import sqlmgr
from extras import embeds

class EventsCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        @bot.event
        async def on_ready():
            logs.info("Bot is running now...")

            logs.info("Listening to views...")

            try:
                bot.add_view(FormUploadView())

                db = sqlmgr.DatabaseManager("data/form_data.db")

                for container in db.get_all_unchecked_forms_uid():
                    uid = container[0]
                    bot.add_view(FormModSubmitView(uid))

            except Exception as e:
                logs.warn(f"Could not listen for views: {e}")

            logs.info("Syncing commands...")

            try:
                await bot.sync_commands()
            except Exception as e:
                logs.warn(f"Could not sync commands: {e}")
            else:
                logs.info("Successfully synced commands")

        @bot.event
        async def on_application_command_error(
            ctx: discord.ApplicationContext, 
            error: discord.DiscordException):

            if isinstance(error, commands.CommandOnCooldown):
                embed = embeds.CooldownEmbed(error.retry_after)
            elif isinstance(error, commands.NotOwner):
                embed = embeds.OwnerOnlyEmbed()
            elif isinstance(error, commands.MissingAnyRole):
                embed = embeds.MissingRolesEmbed()
            elif isinstance(error, commands.MissingPermissions):
                embed = embeds.MissingPermsEmbed()
            elif isinstance(error, commands.BotMissingPermissions):
                embed = embeds.BotMissingPermsEmbed()
            else:
                embed = embeds.UnknownErrorEmbed()
                logs.error(f"Error while invoking command: {" ".join(error.args)}\n{"".join(traceback.format_tb(error.__traceback__))}")

            await ctx.respond(embed=embed, ephemeral=True)
            

def setup(bot: discord.Bot):
    bot.add_cog(EventsCog(bot))
