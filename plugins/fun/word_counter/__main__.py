""" Word Counter """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio

from userge import userge, Message


@userge.on_cmd("wordcount", about={
    'header': "Finds most 25 words used in last 1000 messages",
    'usage': "{tr}wordcount"},
    allow_private=False, allow_via_bot=False)
async def word_count(message: Message):
    """ Finds most words used """
    words = custom()
    await message.edit("```Processed 0 messages...```")
    total = 0
    async for msg in userge.iter_history(message.chat.id, 1000):
        total += 1
        if total % 200 == 0:
            await message.edit(f"```Processed {total} messages...```")
            await asyncio.sleep(0.5)
        if msg.text:
            for word in msg.text.split():
                words[word.lower()] += 1
        if msg.caption:
            for word in msg.caption.split():
                words[word.lower()] += 1
    freq = sorted(words, key=words.get, reverse=True)
    out = "`Word Counter of last 1000 messages.`\n"
    for i in range(25):
        out += f"{i + 1}. **{words[freq[i]]}**: `{freq[i]}`\n"
    await message.edit(out)


class custom(dict):
    def __missing__(self, key):
        return 0
