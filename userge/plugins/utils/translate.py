# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import time
from json import dumps
from emoji import get_emoji_regexp

from googletrans import Translator, LANGUAGES

from userge import userge, Message, Config, pool


@userge.on_cmd("tr", about={
    'header': "Translate the given text using Google Translate",
    'supported languages': dumps(LANGUAGES, indent=4, sort_keys=True),
    'usage': "from english to sinhala\n"
             "{tr}tr -en -si i am userge\n\n"
             "from auto detected language to sinhala\n"
             "{tr}tr -si i am userge\n\n"
             "from auto detected language to preferred\n"
             "{tr}tr i am userge\n\n"
             "reply to message you want to translate from english to sinhala\n"
             "{tr}tr -en -si\n\n"
             "reply to message you want to translate from auto detected language to sinhala\n"
             "{tr}tr -si\n\n"
             "reply to message you want to translate from auto detected language to preferred\n"
             "{tr}tr"}, del_pre=True)
async def translateme(message: Message):
    text = message.filtered_input_str
    flags = message.flags
    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    if not text:
        await message.err(
            text="Give a text or reply to a message to translate!\nuse `.help tr`")
        return
    if len(flags) == 2:
        src, dest = list(flags)
    elif len(flags) == 1:
        src, dest = 'auto', list(flags)[0]
    else:
        src, dest = 'auto', Config.LANG
    text = get_emoji_regexp().sub(u'', text)
    await message.edit("`Translating ...`")
    try:
        reply_text = await _translate_this(text, dest, src)
    except ValueError:
        await message.err(text="Invalid destination language.\nuse `.help tr`")
        return
    source_lan = LANGUAGES[f'{reply_text.src.lower()}']
    transl_lan = LANGUAGES[f'{reply_text.dest.lower()}']
    output = f"**Source ({source_lan.title()}):**`\n{text}`\n\n\
**Translation ({transl_lan.title()}):**\n`{reply_text.text}`"
    await message.edit_or_send_as_file(text=output, caption="translated")


@pool.run_in_thread
def _translate_this(text: str, dest: str, src: str):
    for i in range(10):
        try:
            return Translator().translate(text, dest=dest, src=src)
        except AttributeError:
            if i == 9:
                raise
            time.sleep(0.3)
