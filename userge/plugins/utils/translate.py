# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import time
import asyncio
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
    replied = message.reply_to_message
    is_poll = False

    if replied:
        if replied.poll:
            is_poll = True
            text = f'{replied.poll.question}'
            for option in replied.poll.options:
                text += f'\n,\n{option.text}'
        else:
            text = replied.text or replied.caption
    if not text:
        return await message.err("Give a text or reply to a message to translate!")

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
        return await message.err("Invalid destination language.")

    if is_poll:
        options = reply_text.text.split('\n,\n')
        if len(options) > 1:
            question = options.pop(0)
            await asyncio.gather(
                message.delete(),
                message.client.send_poll(
                    chat_id=message.chat.id,
                    question=question,
                    options=options,
                    is_anonymous=replied.poll.is_anonymous
                )
            )
            return
    source_lan = LANGUAGES[f'{reply_text.src.lower()}']
    transl_lan = LANGUAGES[f'{reply_text.dest.lower()}']
    output = f"**Source ({source_lan.title()}):**`\n{text}`\n\n\
**Translation ({transl_lan.title()}):**\n`{reply_text.text}`"
    await message.edit_or_send_as_file(text=output, caption="translated")


@pool.run_in_thread
def _translate_this(text: str, dest: str, src: str) -> str:
    for i in range(10):
        try:
            return Translator().translate(text, dest=dest, src=src)
        except AttributeError:
            if i == 9:
                raise
            time.sleep(0.3)
