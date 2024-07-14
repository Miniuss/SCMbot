import discord
from discord.ext import commands
from utils import sqlmgr

from configparser import ConfigParser
from os.path import join as path_join
from os.path import exists as path_exists

from json import load as json_load
from json import dump as json_dump

CONFIG = ConfigParser()
CONFIG.read("config.cfg")

ADMIN_ROLES = list(map(int, CONFIG["Perms"]["admin_roles"].replace(" ", "").split(",")))
MSG_CHANNEL = int(CONFIG["Form"]["msg_channel"])
SUBMIT_CHANNEL = int(CONFIG["Form"]["submit_channel"])

class FormsCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    def has_admin_roles(self):
        return commands.has_any_role(*self.admin_roles)

    GROUP = discord.SlashCommandGroup(
        name="form",
        name_localizations={
            "ru": "форма"
        }
    )


    @GROUP.command(
        name="update",
        description="Updates form message with new one",
        name_localizations={
            "ru": "обновить"
        },
        description_localizations={
            "ru": "Обновляет сообщение с формой на новое"
        }
    )
    @commands.has_any_role(*ADMIN_ROLES)
    @commands.cooldown(1, 120, commands.BucketType.guild)
    async def update(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)

        lastmsg_path = path_join("data", "formmsg.txt")
        form_path = path_join("data", "form.json")

        if not path_exists(form_path): # Abort if form.json doesn't exist
            response_embed = discord.Embed(
                title="Файл структуры не найден",
                description="Файл структуры сообщения не найден. Задайте его командой `/form set`",
                color=discord.Color.red()
            )
            await ctx.respond(embed=response_embed, ephemeral=True)

            return
        
        channel = self.bot.get_channel(MSG_CHANNEL)
        
        if path_exists(lastmsg_path):
            with open(lastmsg_path, "r") as f:
                msg_id = int(f.read().replace(" ", "").replace("\n", ""))

                try:
                    message_to_delete = await channel.fetch_message(msg_id)
                except Exception:
                    pass
                else:
                    await message_to_delete.delete()

        embeds = []

        with open(form_path, "r", encoding="UTF-8") as f:
            embeds_list = json_load(f)
            embeds = [discord.Embed.from_dict(e) for e in embeds_list]

        message = await channel.send(embeds=embeds)

        with open(lastmsg_path, "w") as f:
            f.write(str(message.id))

        response_embed = discord.Embed(
            title="Сообщение формы обновлено",
            description=f"Сообщение с формой было обновлено согласно данным, предоставленными вами.\nВы можете увидеть новое сообщение [тут]({message.jump_url})",
            color=discord.Color.green()
        )

        await ctx.respond(embed=response_embed, ephemeral=True)

    @GROUP.command(
        name="set",
        description="Changes form message",
        name_localizations={
            "ru": "установить"
        },
        description_localizations={
            "ru": "Меняет сообщение с формой"
        },
        options=(
            discord.Option(
                discord.SlashCommandOptionType.string,
                min_length=1,
                max_length=256,
                required=True,
                name="title",
                description="Title of the message",
                name_localizations={
                    "ru": "заголовок"
                },
                description_localizations={
                    "ru": "Заголовок сообщения"
                }
            ),
            discord.Option(
                discord.SlashCommandOptionType.string,
                min_length=1,
                max_length=4096,
                required=True,
                name="text",
                description="Text inside of the embed [NOTE: New line = \\n]",
                name_localizations={
                    "ru": "текст"
                },
                description_localizations={
                    "ru": "Текст внутри вложения [ЗАМЕТКА: Новая строка = \\n]"
                }
            ),
            discord.Option(
                discord.SlashCommandOptionType.string,
                min_length=6,
                max_length=6,
                required=False,
                default="FFFFFF",
                name="color",
                description="HEX representation of embed's color (ex. \"FFFFFF\")",
                name_localizations={
                    "ru": "цвет"
                },
                description_localizations={
                    "ru": "Цвет вложения в виде HEX (пр. \"FFFFFF\")"
                }
            ),
            discord.Option(
                discord.SlashCommandOptionType.attachment,
                required=False,
                default=None,
                name="image",
                description="Image that will be attached to the embed",
                name_localizations={
                    "ru": "изображение"
                },
                description_localizations={
                    "ru": "Изображение которое будет крепится к вложению"
                }
            )
        )
    )
    @commands.has_any_role(*ADMIN_ROLES)
    @commands.cooldown(2, 300)
    async def fset(self, ctx: discord.ApplicationContext, title: str, text: str, color: str = "FFFFFF", image: discord.Attachment = None):
        await ctx.defer(ephemeral=True)
        
        embeds = []

        if image is not None:
            e = discord.Embed(
                color=int(str(color), 16)
            )
            e.set_image(url=image.url)

            embeds.append(e.to_dict())

        e = discord.Embed(
            title=title,
            description=text.replace("\\n", "\n"),
            color=int(str(color), 16)
        )

        embeds.append(e.to_dict())


        form_path = path_join("data", "form.json")

        with open(form_path, "w") as f:
            json_dump(embeds, f, indent=4)

        response_embed = discord.Embed(
            title="Новое сообщение установлено",
            description="Ваше новое сообщение с формой было установлено.\nДля того, чтобы изменения вступили в силу, используйте команду `/form update`",
            color=discord.Color.green()
        )

        await ctx.respond(embed=response_embed, ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(FormsCog(bot))
