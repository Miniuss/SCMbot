import discord
from discord.ext import commands
from utils import sqlmgr

from configparser import ConfigParser
from os.path import join as path_join
from os.path import exists as path_exists

from json import load as json_load
from json import dump as json_dump

from time import time as timenow



CONFIG = ConfigParser()
CONFIG.read("config.cfg")

ADMIN_ROLES = list(map(int, CONFIG["Perms"]["admin_roles"].replace(" ", "").split(",")))
NO_FORM_ROLES = list(map(int, CONFIG["Perms"]["no_form_roles"].replace(" ", "").split(",")))

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

        embed = discord.Embed(
            title=f"Заявка {uploader.display_name}",
            color=discord.Color(int("FFFFFF", 16)),
            url=uploader.jump_url
        )

        embed.add_field(
            name="Об участнике",
            value=f"Дата присоединения: <t:{round(uploader.joined_at.timestamp())}:f>\n"
                  f"Дата создания аккаунта: <t:{round(uploader.created_at.timestamp())}:f>\n"
                  f"Упоминание: {uploader.mention}\n"
                  f"Идентификатор пользователя: {uploader.id}",
            inline=False
        )
        embed.add_field(
            name="Ссылка на профиль Steam",
            value=profile_url,
            inline=False
        )
        embed.add_field(
            name="Ссылки на творчества Steam",
            value=content_url,
            inline=False
        )
        embed.add_field(
            name="Претендованные роли",
            value=claimed_roles,
            inline=False
        )

        embed.set_thumbnail(url=uploader.avatar.url)
        embed.set_footer(
            text=f"Идентификатор формы: #{form_id}"
        )

        await channel.send(embed=embed, view=FormModSubmitView(uploader.id))

        response_embed = discord.Embed(
            title="Форма успешно отправлена",
            description="Ваша заявка на получение роли была успешно отправлена "
                        "администрации этого сервера.\n"
                        "Ожидайте ответа!",
            color=discord.Color.green()
        )
        response_embed.set_footer(text=f"Идентификатор формы: #{form_id}")

        await inter.respond(embed=response_embed, ephemeral=True)

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
            embed = discord.Embed(
                title="Вы уже отправляли форму!",
                description="Извините, но вы уже отправляли заявку на получение ролей в данном " 
                            "сервере. Отправить форму можно лишь 1 раз каждому участнику сервера.\n"
                            "Пожалуйста, подождите одобрения формы и выдачи ролей.\n\n"
                            "Свяжитесь с персоналом для возможности переотправки формы.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Ваш идентификатор формы: #{data["id"]}")

            await inter.respond(embed=embed, ephemeral=True)
            return
        
        if any(role.id in NO_FORM_ROLES for role in uploader_roles):
            embed = discord.Embed(
                title="Вам не нужно отправлять заявку",
                description="У вас уже присутствуют роль/роли, которые можно получить за отправку формы",
                color=discord.Color.orange()
            )

            await inter.respond(embed=embed, ephemeral=True)
            return
        
        await inter.response.send_modal(FormModal())

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
            response_embed = discord.Embed(
                title="Нету прав",
                description="У вас недостаточно прав для этого действия",
                color=discord.Color.dark_red()
            )

            await inter.respond(embed=response_embed, ephemeral=True)
            return

        if uploader is None:
            DATABASE.remove_record(uid=self.uid)

            response_embed = discord.Embed(
                title="Участник не на сервере",
                description="Не удалось найти участника на сервере.\n"
                            "Участник, кому пренадлежит данная форма, скорее всего "
                            "вышел с сервера. Форма больше недействительна и будет "
                            "удалена с базы данных бота для возможности участнику её "
                            "переотправить и в целях оптимизации памяти.",
                color=discord.Color.red()
            )

            await inter.respond(response_embed)
            self.disable_all_items()

            return
        
        await inter.response.defer()

        DATABASE.role_approval(approver.id, uid=self.uid)

        user_embed = discord.Embed(
            title=f"Ваша форма в {inter.guild.name} была принята!",
            description=f"Администратор **{approver.global_name}** принял вашу форму!\n"
                        f"Пожалуйста, ожидайте получение роли",
            color=discord.Color.green()
        )
        user_embed.set_footer(text=f"Идентификатор подтвердителя: {approver.id}")

        dm_channel = await uploader.create_dm()
        await dm_channel.send(embed=user_embed)

        response_embed = discord.Embed(
            title=f"{approver.global_name} подтвердил эту форму",
            description=f"Идентификатор подтвердителя: {approver.id}",
            color=discord.Color.dark_green()
        )

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
            response_embed = discord.Embed(
                title="Нету прав",
                description="У вас недостаточно прав для этого действия",
                color=discord.Color.dark_red()
            )

            await inter.respond(embed=response_embed, ephemeral=True)
            return

        if uploader is None:
            DATABASE.remove_record(uid=self.uid)

            response_embed = discord.Embed(
                title="Участник не на сервере",
                description="Не удалось найти участника на сервере.\n"
                            "Участник, кому пренадлежит данная форма, скорее всего "
                            "вышел с сервера. Форма больше недействительна и будет "
                            "удалена с базы данных бота для возможности участнику её "
                            "переотправить и в целях оптимизации памяти.",
                color=discord.Color.red()
            )

            await inter.respond(response_embed)
            self.disable_all_items()

            return
        
        await inter.response.defer()

        DATABASE.role_approval(approver.id, uid=self.uid)

        user_embed = discord.Embed(
            title=f"Ваша форма в {inter.guild.name} отклонена!",
            description=f"Администратор **{approver.global_name}** отклонил вашу форму!",
            color=discord.Color.red()
        )
        user_embed.set_footer(text=f"Идентификатор отклонителя: {approver.id}")

        dm_channel = await uploader.create_dm()
        await dm_channel.send(embed=user_embed)

        response_embed = discord.Embed(
            title=f"{approver.global_name} отклонил эту форму",
            description=f"Идентификатор отклонителя: {approver.id}",
            color=discord.Color.dark_red()
        )

        self.disable_all_items()

        await inter.message.edit(view=self)
        await inter.respond(embed=response_embed)



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

        message = await channel.send(embeds=embeds, view=FormUploadView())

        with open(lastmsg_path, "w") as f:
            f.write(str(message.id))

        response_embed = discord.Embed(
            title="Сообщение формы обновлено",
            description=f"Сообщение с формой было обновлено согласно данным, предоставленными "
                        f"вами.\nВы можете увидеть новое сообщение [тут]({message.jump_url})",
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
            description="Ваше новое сообщение с формой было установлено.\n"
                        "Для того, чтобы изменения вступили в силу, используйте команду "
                        "`/form update`",
            color=discord.Color.green()
        )

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
            embed = discord.Embed(
                title="Нету аргументов",
                description="Хотя-бы один из аргументов команды должен быть равен чему-то",
                color=discord.Color.orange()
            )

            await ctx.respond(embed=embed, ephemeral=True)
            return

        try:
            form_id = int(form_id)
            user_id = int(user_id)
        except ValueError:
            embed = discord.Embed(
                title="Неверное значение ИД формы/пользователя",
                description="ИД должно быть целым числом!",
                color=discord.Color.dark_red()
            )

            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        data = DATABASE.exctract_record_data(form_id=form_id, uid=user_id)

        if data is None:
            embed = discord.Embed(
                title="Данные отсутствуют",
                color=discord.Color.orange()
            )

            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        id = data["id"]
        upload_time = data["upload_time"]
        steam_profile_url = data["steam_profile_url"]
        steam_content_url = data["steam_content_url"]
        claimed_roles = data["claimed_roles"]
        
        uploader = data["uid"]
        approver = data["approver_uid"] or "Нету"


        embed = discord.Embed(
            title=f"Форма #{id}",
            description=f"Дата загрузки: <t:{upload_time}:f>\n"
                        f"ИД отправителя: {uploader}\n"
                        f"ИД подтвердителя/отклонителя: {approver}",
            color=discord.Color(int("FFFFFF", 16))
        )
        embed.add_field(
            name="Ссылка на профиль Steam",
            value=steam_profile_url,
            inline=False
        )
        embed.add_field(
            name="Ссылки на творчества Steam",
            value=steam_content_url,
            inline=False
        )
        embed.add_field(
            name="Претендованные роли",
            value=claimed_roles,
            inline=False
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
            embed = discord.Embed(
                title="Нету аргументов",
                description="Хотя-бы один из аргументов команды должен быть равен чему-то",
                color=discord.Color.orange()
            )

            await ctx.respond(embed=embed, ephemeral=True)
            return

        try:
            form_id = int(form_id)
            user_id = int(user_id)
        except ValueError:
            embed = discord.Embed(
                title="Неверное значение ИД формы/пользователя",
                description="ИД должно быть целым числом!",
                color=discord.Color.dark_red()
            )

            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        DATABASE.remove_record(form_id=form_id, uid=user_id)

        embed = discord.Embed(
            title="Данные формы были удалены",
            color=discord.Color.red()
        )

        await ctx.respond(embed=embed, ephemeral=True)



def setup(bot: discord.Bot):
    bot.add_cog(FormsCog(bot))
