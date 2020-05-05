# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import random
import asyncio

from pyrogram.errors.exceptions.bad_request_400 import YouBlockedUser

from userge import userge, Message


@userge.on_cmd("carbon", about={
    'header': "create a carbon",
    'usage': "{tr}carbon [text | reply to msg]"})
async def carbon_(message: Message):
    replied = message.reply_to_message
    if replied:
        text = replied.text
    else:
        text = message.input_str
    if not text:
        await message.err("input not found!")
        return
    await message.edit("`creating a carbon...`")
    async with userge.conversation("CarbonNowShBot", timeout=30) as conv:
        try:
            await conv.send_message(text)
        except YouBlockedUser:
            await message.edit('first **unblock** @CarbonNowShBot')
            return
        response = await conv.get_response(mark_read=True)
        while not response.reply_markup:
            response = await conv.get_response(mark_read=True)
        await response.click(x=random.randint(0, 2), y=random.randint(0, 8))
        response = await conv.get_response(mark_read=True)
        while not response.media:
            response = await conv.get_response(mark_read=True)
        caption = "\n".join(response.caption.split("\n")[0:2])
        file_id = response.document.file_id
        await message.delete()
        await userge.send_document(chat_id=message.chat.id,
                                   document=file_id,
                                   caption='`' + caption + '`',
                                   reply_to_message_id=replied.message_id if replied else None)
