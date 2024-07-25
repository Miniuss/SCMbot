from discord import Embed, Color
from discord import Member


# ERROR RELATED EMBEDS

class ErrorEmbed(Embed): # Parent of all error related embeds
    def __init__(self, err_info: str):
        super().__init__()

        self.title = "Ой! ⛔"
        self.description = err_info
        self.color = Color.dark_red()


class CooldownEmbed(ErrorEmbed):
    def __init__(self, cooldown: int | float):
        cooldown = int(cooldown)

        mins = cooldown // 60
        secs = cooldown % 60

        formatted_cooldown = f"{str(mins)}:{str(secs).zfill(2)}"

        err_info = (
            "Вы используете команду слишком часто!\n"
            f"Попробуйте снова через `{formatted_cooldown}`"
        )

        super().__init__(err_info)

class OwnerOnlyEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(
            "Данная команда доступна только владельцу бота!"
        )

class MissingRolesEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(
            "У вас нету необходимых ролей для выполнения этой команды!"
        )

class MissingPermsEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(
            "У вас недостаточно прав для выполнения данной команды"
        )

class BotMissingPermsEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(
            (
                "**Бот не владеет необходимыми правами для выполнения этой команды**\n"
                "Это означает, что при установке бота были отключены некоторые права, "
                "необходимые для работоспособности бота\n\n"
                "Пожалуйста, передайте данное сообщение владельцу сервера!"
            )
        )

class UnknownErrorEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(
            (
                "**Произошла внутренняя неизвестная ошибка!**\n"
                "Это не ваша вина! Данные об ошибке были отправлены разработчику для "
                "анализа\n\n"
                "Извиняемся за предоставленные неудобства!"
            )
        )


# FORM RELATED EMBEDS

class FormSubmittedInfoEmbed(Embed):
    def __init__(
            self,
            form_id: int,
            uploader: Member,
            profile_url: str = "Нет данных",
            content_url: str = "Нет данных",
            claimed_roles : str = "Нет данных"):
        
        super().__init__()

        self.title = f"Заявка {uploader.display_name}"
        self.url = f"https://discord.com/users/{uploader.id}"

        self.color = Color(int("FFFFFF", 16))
        self.set_footer(text=f"Идентификатор формы: #{form_id}")

        self.set_thumbnail(url=uploader.avatar.url)

        self.add_field(
            name="Об участнике",
            value=(
                f"Дата захода на сервер: <t:{round(uploader.joined_at.timestamp())}:f>\n"
                f"Дата создания аккаунта: <t:{round(uploader.created_at.timestamp())}:f>\n"
                f"Упоминание: {uploader.mention}\n"
                f"Идентификатор пользователя: `{uploader.id}`"
            ),
            inline=False
        )


        self.add_field(
            name="Ссылка на профиль Steam",
            value=profile_url,
            inline=False
        )

        self.add_field(
            name="Ссылки на творчества Steam",
            value=content_url,
            inline=False
        )

        self.add_field(
            name="Претендованные роли",
            value=claimed_roles,
            inline=False
        )

class NoDataFormViewEmbed(Embed):
    def __init__(self):
        super().__init__()

        self.title = "Данные отсутствуют"
        self.color = Color.orange()

class FormViewDataEmbed(Embed):
    def __init__(
            self,
            form_id: int,
            uid: int,
            approver_uid: int,
            upload_time: int | float,
            profile_url: str = "Нет данных",
            content_url: str = "Нет данных",
            claimed_roles : str = "Нет данных"):
        
        upload_time = int(upload_time)
        
        super().__init__()

        self.title = f"Форма #{form_id}"
        self.color = Color(int("FFFFFF", 16))

        self.description = (
            f"Дата загрузки формы: <t:{upload_time}:f>\n\n"
            f"ИД отправителя: `{uid}`\n"
            f"> Упоминание: <@{uid}>\n\n"
            f"ИД проверяющего: `{approver_uid}`\n"
            f"> Упоминание: <@{approver_uid}>"
        )


        self.add_field(
            name="Ссылка на профиль Steam",
            value=profile_url,
            inline=False
        )

        self.add_field(
            name="Ссылки на творчества Steam",
            value=content_url,
            inline=False
        )

        self.add_field(
            name="Претендованные роли",
            value=claimed_roles,
            inline=False
        )

class FormDeletedEmbed(Embed):
    def __init__(self):
        super().__init__()

        self.title = "Данные формы были удалены"
        self.color = Color.red()


class FormSubmitSuccessEmbed(Embed):
    def __init__(self, form_id: int | None = None):
        super().__init__()

        self.title = "Форма успешно отправлена"
        self.color = Color.green()

        self.description = (
            "Ваша форма была успешно отправлена администрации сервера на "
            "рассмотрение. Бот даст вам знать, когда вынесут решение.\n\n"
            "Ожидайте ответа!"
        )

        if form_id is not None:
            self.set_footer(text=f"Идентификатор формы: #{form_id}")

class FormAlreadySubmittedEmbed(Embed):
    def __init__(self, form_id: int | None = None):
        super().__init__()

        self.title = "Вы уже отправляли форму!"
        self.color = Color.red()

        self.description = (
            "У вас уже есть отправленная форма на данном сервере!\n\n"
            "Каждый участник может отправить форму лишь 1 раз. Если вы "
            "желаете переотправить форму для поправки, обратитесь к администрации "
            "сервера, сообщите идентификатор вашей формы и что вы хотите с ней сделать."
        )

        if form_id is not None:
            self.set_footer(text=f"Идентификатор формы: #{form_id}")

class FromSubmitterHasRoleEmbed(Embed):
    def __init__(self):
        super().__init__()

        self.title = "Вам не нужно отправлять форму!"
        self.color = Color.orange()

        self.description = (
            "У вас уже присутствует роль/роли, которые можно получить за отправку "
            "формы!"
        )

class FormNoPermsEmbed(Embed):
    def __init__(self):
        super().__init__()

        self.title = "Нету прав"
        self.color = Color.dark_red()

        self.description = "У вас недостаточно прав для этого действия"

class FormOwnerNotFoundEmbed(Embed):
    def __init__(self):
        super().__init__()

        self.title = "Участник не найден"
        self.color = Color.orange()

        self.description = (
            "Не удалось найти участника, кому пренадлежит форма!\n"
            "Это может быть по причине выхода участника с сервера, или "
            "бот попросту не смог его найти.\n"
            "Если вы уверены, что участник вышел, просьба удалить форму командой "
            "`/form delete`"
        )

class FormApprovedEmbed(Embed):
    def __init__(self, guild_name: str, approver: Member):
        super().__init__()

        self.title = "Ваша форма была одобрена!"
        self.color = Color.green()

        self.set_footer(text=f"Идентификатор проверяющего: {approver.id}")

        self.description = (
            f"Ваша форма на сервере **{guild_name}** была одобрена "
            f"администратором {approver.global_name}!\n"
            "Ожидайте получения роли!"
        )

class FormDeniedEmbed(Embed):
    def __init__(self, guild_name: str, approver: Member):
        super().__init__()

        self.title = "Ваша форма была отклонена!"
        self.color = Color.red()

        self.set_footer(text=f"Идентификатор проверяющего: {approver.id}")

        self.description = (
            f"Ваша форма на сервере **{guild_name}** была отклонена "
            f"администратором {approver.global_name}!\n"
        )

class MemberApprovedFormEmbed(Embed):
    def __init__(self, approver: Member):
        super().__init__()

        self.title = f"{approver.global_name} подтвердил эту форму"
        self.color = Color.dark_green()

        self.description = f"Идентифиактор проверяющего: `{approver.id}`"

class MemberDeniedFormEmbed(Embed):
    def __init__(self, approver: Member):
        super().__init__()

        self.title = f"{approver.global_name} отклонил эту форму"
        self.color = Color.dark_red()

        self.description = f"Идентифиактор проверяющего: `{approver.id}`"


class StructureFileNotFoundEmbed(Embed):
    def __init__(self):
        super().__init__()

        self.title = "Файл структуры не найден!"
        self.color = Color.red()

        self.description = "Файл структуры сообщения не найден. Задайте его командой `/form set`"

class MessageUpdatedEmbed(Embed):
    def __init__(self):
        super().__init__()

        self.title = "Сообщение с формой обновлено"
        self.color = Color.green()

        self.description = (
            "Сообщение с формой было обновлено согласно данным, предоставленными "
            "вами."
        )

class NewStructureSetEmbed(Embed):
    def __init__(self):
        super().__init__()
        
        self.title = "Новое сообщение установлено"
        self.color = Color.green()

        self.description = (
            "Ваше новое сообщение с формой было установлено.\n"
            "Для того, чтобы изменения вступили в силу, используйте команду "
            "`/form update`"
        )


class MissingArgumentsEmbed(Embed):
    def __init__(self):
        super().__init__()

        self.title = "Нету аргументов"
        self.color = Color.dark_red()

        self.description = "Хотя-бы один из аргументов команды должен быть равен чему-то"

class IncorrectIdEmbed(Embed):
    def __init__(self):
        super().__init__()

        self.title = "Неверное значение ИД формы/пользователя"
        self.color = Color.dark_red()

        self.description = "ИД должно быть целым числом!"
