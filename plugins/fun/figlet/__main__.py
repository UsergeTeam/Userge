""" create figlet text """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

# by Alone and krishna

from pyfiglet import Figlet

from userge import userge, Message


@userge.on_cmd("figlet", about={
    'header': "Figlet",
    'description': "Make Fancy Style text using Figlet",
    'usage': "{tr}figlet font_name | [text | reply]",
    'Fonts': "<code>Check this</code> "
             "<a href='https://telegra.ph/Figlet-List-Of-Fonts-07-03'>link</a>"
             " <code>to know available fonts</code>"})
async def figlet_(message: Message):
    args = message.input_or_reply_str
    if not args:
        await message.edit(
            "**Do You think this is Funny?**\n\n"
            "__Try this Blek Mejik:__\n\n"
            "```.help .figlet```")
        await message.reply_sticker(sticker="CAADBAAD1AIAAnV4kzMWpUTkTJ9JwRYE")
        return
    if "|" in message.input_or_reply_str:
        style, text = message.input_str.split('|')
        custom_fig = Figlet(font=style.strip())
        await message.edit(f"```{custom_fig.renderText(text.strip())}```")
        return
    str_ = ' '.join(args)
    custom_fig = Figlet(font='xsans')
    await message.edit(f"```{custom_fig.renderText(str_)}```")
