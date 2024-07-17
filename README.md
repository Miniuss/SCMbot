# SCMbot
Open-source russian bot for Steam Content Makers server with ability to create forms and store their data.

> [!NOTE]
> Русская версия доступна [здесь](README_ru.md)

> [!CAUTION]
> This bot is designed to work for single server only. Running it in different servers may cause issues

## Features
- Discord modal form editor
- SQLite form data storage
- Configurable, with logs


## Dependencies
All dependencies are written in [requirements.txt](requirements.txt)


## How to configure
This paragraph explains what each config.cfg parameter does.

### [Login]
- **token:** Bot's token. Required for bot to log into Discord. \
  Example: `token=MY_TOKEN`

### [Perms]
- **admin_roles:** List of role ids that bot will consider Administrators. Admins have permissions for special commands. This value is separated with `,` \
  Example: `admin_roles=129528543536,219391248849`

- **no_form_roles:** List of role ids that bot will not allow to write form. This value is separated with `,` \
  Example: `no_form_roles=1249285259643,32429534563,34698459064`

### [Form]
- **msg_channel:** Channel id where bot will send form message. \
  Example: `msg_channel=158258349063`

- **submit_channel:** Channel id where bot will display submited forms. \
  Example: `submit_channel=25934560645`


## Available commands

### Base
- **/ping:** Displays bot's ping in the chat (ephemeral message)

- **/logs [OWNER ONLY]:** Sends `logs.log` file in chat (ephemeral message)

- **/shutdown [OWNER ONLY]:** Shuts bot down

### Forms
- **/form update [ADMIN ONLY]:** Updates or sends form message according to `form.json` file

- **/form set [ADMIN ONLY]:** Updates `form.json` according to arguments
    - title \<str\>: Title of embed
    - text \<str\>: Description of embed
    - color \<str\>: HEX color of embed
    - image \<discord.Attachment\>: Image that will be displayed on separate topmost embed

- **/form view [ADMIN ONLY]:** Looks for form  according to arguments, and then outputs data in chat (ephemeral message)
    - form_id \<str\> -> \<int\>: Integer ID of form (gets converted to int later)
    - user_id \<str\> -> \<int\>: Integer ID of user that the form belongs to

- **/form delete [ADMIN ONLY]:** Looks for form according to arguments, then deletes it from database
    - form_id \<str\> -> \<int\>: Integer ID of form (gets converted to int later)
    - user_id \<str\> -> \<int\>: Integer ID of user that the form belongs to

# License
This project is licensed under MIT License. [Read license here](LICENSE)
