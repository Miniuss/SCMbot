import discord
from discord.ext import commands

from utils import sqlmgr
from extras import embeds, views

from configparser import ConfigParser
from os.path import join as path_join
from os.path import exists as path_exists

from json import load as json_load
from json import dump as json_dump



CONFIG = ConfigParser()
CONFIG.read("config.cfg")

ADMIN_ROLES = list(map(int, CONFIG["Perms"]["admin_roles"].replace(" ", "").split(",")))

MSG_CHANNEL = int(CONFIG["Form"]["msg_channel"])

DATABASE = sqlmgr.DatabaseManager("data/form_data.db")



class FormsCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


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
            response_embed = embeds.StructureFileNotFoundEmbed()
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

        _embeds = []

        with open(form_path, "r", encoding="UTF-8") as f:
            embeds_list = json_load(f)
            _embeds = [discord.Embed.from_dict(e) for e in embeds_list]

        message = await channel.send(embeds=_embeds, view=views.FormUploadView())

        with open(lastmsg_path, "w") as f:
            f.write(str(message.id))

        response_embed = embeds.MessageUpdatedEmbed()

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
        
        _embeds = []

        if image is not None:
            e = discord.Embed(
                color=int(str(color), 16)
            )
            e.set_image(url=image.url)

            _embeds.append(e.to_dict())

        e = discord.Embed(
            title=title,
            description=text.replace("\\n", "\n"),
            color=int(str(color), 16)
        )

        _embeds.append(e.to_dict())


        form_path = path_join("data", "form.json")

        with open(form_path, "w") as f:
            json_dump(_embeds, f, indent=4)

        response_embed = embeds.NewStructureSetEmbed()

        await ctx.respond(embed=response_embed, ephemeral=True)



    @GROUP.command(
        name="view",
        description="Find and view form info",
        name_localizations={
            "ru": "посмотреть"
        },
        description_localizations={
            "ru": "Находит и показывает информацию о форме"
        },
        options=(
            discord.Option(
                discord.SlashCommandOptionType.string,
                min_length=1,
                max_length=40,
                required=False,
                default=-1,
                name="form_id",
                description="Integer ID of the form",
                name_localizations={
                    "ru": "ид_формы"
                },
                description_localizations={
                    "ru": "Целочисленный идентификатор формы"
                }
            ),
            discord.Option(
                discord.SlashCommandOptionType.string,
                min_length=1,
                max_length=40,
                required=False,
                default=-1,
                name="user_id",
                description="Integer ID of the user",
                name_localizations={
                    "ru": "ид_пользователя"
                },
                description_localizations={
                    "ru": "Целочисленный идентификатор пользователя"
                }
            )
        )
    )
    @commands.has_any_role(*ADMIN_ROLES)
    async def fview(self, ctx: discord.ApplicationContext, form_id: str = -1, user_id: str = -1):
        if form_id == -1 and user_id == -1:
            embed = embeds.MissingArgumentsEmbed()

            await ctx.respond(embed=embed, ephemeral=True)
            return

        try:
            form_id = int(form_id)
            user_id = int(user_id)
        except ValueError:
            embed = embeds.IncorrectIdEmbed()

            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        data = DATABASE.exctract_record_data(form_id=form_id, uid=user_id)

        if data is None:
            embed = embeds.NoDataFormViewEmbed()

            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        id = data["id"]
        upload_time = data["upload_time"]
        steam_profile_url = data["steam_profile_url"]
        steam_content_url = data["steam_content_url"]
        claimed_roles = data["claimed_roles"]
        
        uploader = data["uid"]
        approver = data["approver_uid"] or "Нету"


        embed = embeds.FormViewDataEmbed(
            id,
            uploader,
            approver,
            upload_time,
            steam_profile_url,
            steam_content_url,
            claimed_roles
        )

        await ctx.respond(embed=embed, ephemeral=True)



    @GROUP.command(
        name="delete",
        description="Deletes form data forever",
        name_localizations={
            "ru": "удалить"
        },
        description_localizations={
            "ru": "Удаляет навсегда данные формы"
        },
        options=(
            discord.Option(
                discord.SlashCommandOptionType.string,
                min_length=1,
                max_length=40,
                required=False,
                default=-1,
                name="form_id",
                description="Integer ID of the form",
                name_localizations={
                    "ru": "ид_формы"
                },
                description_localizations={
                    "ru": "Целочисленный идентификатор формы"
                }
            ),
            discord.Option(
                discord.SlashCommandOptionType.string,
                min_length=1,
                max_length=40,
                required=False,
                default=-1,
                name="user_id",
                description="Integer ID of the user",
                name_localizations={
                    "ru": "ид_пользователя"
                },
                description_localizations={
                    "ru": "Целочисленный идентификатор пользователя"
                }
            )
        )
    )
    @commands.has_any_role(*ADMIN_ROLES)
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def fdelete(self, ctx: discord.ApplicationContext, form_id: str = -1, user_id: str = -1):
        if form_id == -1 and user_id == -1:
            embed = embeds.MissingArgumentsEmbed()

            await ctx.respond(embed=embed, ephemeral=True)
            return

        try:
            form_id = int(form_id)
            user_id = int(user_id)
        except ValueError:
            embed = embeds.IncorrectIdEmbed()

            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        DATABASE.remove_record(form_id=form_id, uid=user_id)

        embed = embeds.FormDeletedEmbed()

        await ctx.respond(embed=embed, ephemeral=True)



def setup(bot: discord.Bot):
    bot.add_cog(FormsCog(bot))
