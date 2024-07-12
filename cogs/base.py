import discord
from discord.ext import commands
from os.path import exists as path_exists
from utils.logs import info as loginfo

class BaseCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot



    @commands.slash_command(
        name="ping",
        description="Displays bot's ping",
        name_localizations={
            "ru": "пинг"
        },
        description_localizations={
            "ru": "Отображает пинг бота"
        }
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx: discord.ApplicationContext):
        ping = round(self.bot.latency * 1000)

        await ctx.respond(content=f"Соединение бота: {ping}ms", ephemeral=True)



    @commands.slash_command(
        name="logs",
        description="Sends logs file",
        name_localizations={
            "ru": "логи"
        },
        description_localizations={
            "ru": "Отправляет файл с логами"
        }
    )
    @commands.is_owner()
    async def logs(self, ctx: discord.ApplicationContext):
        if path_exists("logs.log"):
            file = discord.File("logs.log", filename="logs.log")

            await ctx.respond(file=file, ephemeral=True)
        else:
            await ctx.respond(content="Логи отсутствуют", ephemeral=True)



    @commands.slash_command(
        name="shutdown",
        description="Shuts bot down",
        name_localizations={
            "ru": "выключение"
        },
        description_localizations={
            "ru": "Выключает бота"
        }
    )
    @commands.is_owner()
    async def shutdown(self, ctx: discord.ApplicationContext):
        loginfo("Prompted shutdown")

        try:
            await ctx.respond("Идёт выключение...", ephemeral=True)
            await self.bot.close()
        except Exception: # This way, if response or disconnect somehow fails,
            pass          # bot will still shut down

        quit(0)

def setup(bot: discord.Bot):
    bot.add_cog(BaseCog(bot))
