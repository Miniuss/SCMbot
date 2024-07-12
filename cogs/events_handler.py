import discord
from discord.ext import commands
from utils import logs
import traceback

class EventsCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        @bot.event
        async def on_ready():
            logs.info("Bot is running now...")
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
            
            embed = discord.Embed(
                title="Ой! ⛔",
                color=discord.Color.dark_red()
            )

            if isinstance(error, commands.CommandOnCooldown):
                minutes = str(int(error.retry_after // 60))
                seconds = str(int(error.retry_after % 60)).zfill(2)

                embed.description = f"Вы используете команду слишком часто!\nПопробуйте снова через ``{minutes}:{seconds}``"
            elif isinstance(error, commands.NotOwner):
                embed.description = "Данная команда доступна только владельцу сервера!"
            elif isinstance(error, commands.MissingAnyRole):
                embed.description = "Вы не владеете необходимыми ролями для использования этой команды!"
            elif isinstance(error, commands.MissingRole):
                embed.description = "Вы не владеете необходимой ролью для использования этой команды!"
            elif isinstance(error, commands.MissingPermissions):
                embed.description = "Вы не владеете необходимыми правами для использования этой команды!"
            elif isinstance(error, commands.BotMissingPermissions):
                embed.description = "Бот не владеет необходимыми правами для выполнения данной команды! Это значит, что при установке бота владелец сервера убрал определённые права у бота."
                embed.set_footer(text="Передайте это сообщение владельцу сервера")
            else:
                embed.description = "Неизвестная ошибка!\nИнформация об ошибке была отправлена разработчику. С вашей стороны не требуется действий."
                logs.error(f"Error while invoking command: {" ".join(error.args)}\n{"".join(traceback.format_tb(error.__traceback__))}")

            await ctx.respond(embed=embed, ephemeral=True)
            

def setup(bot: discord.Bot):
    bot.add_cog(EventsCog(bot))
