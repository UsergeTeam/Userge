""" spam """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import os

from userge import userge, Message, config
from userge.utils import get_file_id_of_media

S_LOG = userge.getCLogger(__name__)


@userge.on_cmd("spam", about={
    'header': "Spam some Messages",
    'description': "Message Spam module just for fun."
                   "Btw Don't over use this plugin or get"
                   "ready for account ban or flood waits. "
                   "For spamming text use '|' to separate count and text.",
    'usage': "{tr}spam [spam count] | [spam message/reply to a media] | [Optional: delay]",
    'examples': "**For Text:** `{tr}spam 2 | Durov will ban me for using this plugin`"})
async def spam(message: Message):
    replied = message.reply_to_message
    delay = str(0.1)
    is_str = "|" in message.input_str
    if (replied and replied.media and not is_str):
        if not os.path.isdir(config.Dynamic.DOWN_PATH):
            os.makedirs(config.Dynamic.DOWN_PATH)
        if replied.sticker:
            to_spam = replied.sticker.file_id
            count = message.input_str
            if " " in count:
                count, delay = count.split(" ", maxsplit=1)
            try:
                count = int(count)
                delay = float(delay) if '.' in delay else int(delay)
            except ValueError as e:
                await message.edit(e)
                await message.reply_sticker(sticker="CAADAQADzAADiO9hRu2b2xyV4IbAFgQ")
                return
            await message.edit(f"Spamming {count} Time")
            for _ in range(count):
                if message.process_is_canceled:
                    return await message.edit("`Process Cancelled`")
                await message.client.send_sticker(sticker=to_spam, chat_id=message.chat.id)
                await asyncio.sleep(delay)
            await S_LOG.log(f"Spammed Sticker in Chat» {message.chat.title}, {count} times")
            await message.delete()
        elif (replied.animation or replied.video or replied.photo or replied.document):
            to_spam = get_file_id_of_media(replied)
            count = message.input_str
            if " " in count:
                count, delay = count.split(" ", maxsplit=1)
            try:
                count = int(count)
                delay = float(delay) if '.' in delay else int(delay)
            except ValueError as e:
                await message.edit(e)
                await message.reply_sticker(sticker="CAADAQADzAADiO9hRu2b2xyV4IbAFgQ")
                return
            await message.edit(f"Spamming {count} times")
            for _ in range(count):
                if message.process_is_canceled:
                    return await message.edit("`Process Cancelled`")
                await message.client.send_cached_media(message.chat.id, to_spam)
                await asyncio.sleep(delay)
            await S_LOG.log(f"Spammed Media in Chat» {message.chat.title}, {count} times")
            await message.delete()
    elif (replied and replied.text and not is_str):
        count = message.input_str
        if " " in count:
            count, delay = count.split(" ", maxsplit=1)
        try:
            count = int(count)
            delay = float(delay) if '.' in delay else int(delay)
        except ValueError as e:
            await message.edit(e)
            await message.reply_sticker(sticker="CAADAQADzAADiO9hRu2b2xyV4IbAFgQ")
            return
        await message.edit(f"Spamming {count} times")
        for _ in range(count):
            if message.process_is_canceled:
                return await message.edit("`Process Cancelled`")
            await message.client.send_message(text=replied.text, chat_id=message.chat.id)
            await asyncio.sleep(delay)
        await S_LOG.log(f"Spammed Text in Chat» {message.chat.title}, {count} times")
        await message.delete()
    elif is_str:
        spam_count, spam_text = message.input_str.split("|", maxsplit=1)
        if '|' in spam_text:
            spam_text, delay = spam_text.split("|", maxsplit=1)
        try:
            sc = int(spam_count)
            delay = float(delay) if '.' in delay else int(delay)
        except ValueError as e:
            await message.edit(e)
            await message.reply_sticker(sticker="CAADAQADzAADiO9hRu2b2xyV4IbAFgQ")
            return
        await message.edit(f"Spamming {sc} times")
        for _ in range(sc):
            if message.process_is_canceled:
                return await message.edit("`Process Cancelled`")
            await message.client.send_message(text=spam_text, chat_id=message.chat.id)
            await asyncio.sleep(delay)
        await S_LOG.log(f"Spammed Text in Chat» {message.chat.title}, {sc} times")
        await message.delete()
    else:
        await message.edit("Well it doesn't work that way")
        await message.reply_sticker(sticker="CAADAQAD6gADfAVQRnyVSb3GhGT4FgQ")
