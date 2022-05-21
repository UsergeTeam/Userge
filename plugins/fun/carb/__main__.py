""" create carbon """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# Userge Plugin for carbon.now.sh with custom theme and background colour support
# Based on https://github.com/cyberboysumanjay/Carbon-API
# Author: Sumanjay (https://github.com/cyberboysumanjay) (@cyberboysumanjay)
#
# All rights reserved.

import requests

from userge import userge, Message


@userge.on_cmd("carb", about={
    'header': "Create a carbon",
    'usage': "{tr}carb [text or reply to msg | theme-name | colour code]",
    'examples': "{tr}carb Carbon Plugin by Sumanjay | one-dark | #FF0000",
    'themes': [
        '3024-night', 'a11y-dark', 'blackboard', 'base16-dark', 'base16-light',
        'cobalt', 'dracula', 'duotone-dark', 'hopscotch', 'lucario', 'material',
        'monokai', 'night-owl', 'nord', 'oceanic-next', 'one-light', 'one-dark',
        'panda-syntax', 'paraiso-dark', 'seti', 'shades-of-purple', 'solarized-dark',
        'solarized-light', 'synthwave-84', 'twilight', 'verminal', 'vscode',
        'yeti', 'zenburn']})
async def carb(message: Message):
    # Setting Default Theme and Background Colour
    theme = 'dracula'
    bg = "rgba(144, 19, 254, 100)"
    themes = [
        '3024-night', 'a11y-dark', 'blackboard', 'base16-dark', 'base16-light',
        'cobalt', 'dracula', 'duotone-dark', 'hopscotch', 'lucario', 'material',
        'monokai', 'night-owl', 'nord', 'oceanic-next', 'one-light', 'one-dark',
        'panda-syntax', 'paraiso-dark', 'seti', 'shades-of-purple', 'solarized-dark',
        'solarized-light', 'synthwave-84', 'twilight', 'verminal', 'vscode',
        'yeti', 'zenburn']

    replied = message.reply_to_message
    if replied:
        text = replied.text
        args = message.input_str.split('|')
    else:
        text = message.input_str
        args = text.split('|')

    if len(args) > 0:
        for arg in args:
            arg = arg.strip()
            if arg.lower().replace(" ", "-") in themes:
                theme = arg.lower()
            elif arg.startswith("#") or arg.startswith("rgb"):
                if arg[0] == "#" and len(arg) == 7:
                    arg = arg[1:]
                bg = arg
            elif len(arg) > 0:
                text = arg

    if not text:
        await message.err("Input not found!")
        return
    await message.edit("⚡️ Carbonizing ⚡️")
    try:
        carbon_result = requests.get(
            "https://sumanjay.up.railway.app/carbon/?"
            f"text={text}&theme={theme}&bg={bg}").json()
        await message.client.send_photo(chat_id=message.chat.id, photo=carbon_result['link'])
        await message.delete()
    except Exception:
        await message.edit("API is Down! Try again later.")
