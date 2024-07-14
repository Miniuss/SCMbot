import discord
from utils import logs
from configparser import ConfigParser
from os import listdir

def main():
    CONFIG = ConfigParser()
    CONFIG.read("config.cfg")

    activity = discord.Game(name="Арбузный")
    bot = discord.Bot(activity=activity, status=discord.Status.idle)

    logs.info("Loading bot's extensions...")

    for filename in listdir("cogs"):
        if filename[-3:] == ".py":
            logs.info(f"Loading {filename}...")

            try:
                bot.load_extension(f"cogs.{filename[:-3]}")
            except Exception as e:
                logs.warn(f"Failed to load extension: {e}")
            else:
                logs.info("Successfully loaded extension")

    logs.info("Launching the bot")

    try:
        bot.run(bot.config["Login"]["token"])
    except Exception as e:
        logs.error(f"Could not launch bot: {e}")
        quit(1)

if __name__ == "__main__":
    main()
