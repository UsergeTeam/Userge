# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import asyncio

from userge import userge, Message


@userge.on_cmd("quote", about={
    'header': "Quote a message",
    'usage': "{tr}quote [text or reply to msg]"})
async def quotecmd(message: Message):
    """quotecmd"""
    asyncio.create_task(message.delete())
    args = message.input_str
    replied = message.reply_to_message
    async with userge.conversation('QuotLyBot') as conv:
        if replied:
            await userge.forward_messages(chat_id=conv.chat_id,
                                          from_chat_id=message.chat.id,
                                          message_ids=replied.message_id)
        else:
            await conv.send_message(args)
        quote = await conv.get_response(mark_read=True)
        await userge.forward_messages(chat_id=message.chat.id,
                                      from_chat_id=conv.chat_id,
                                      message_ids=quote.message_id,
                                      as_copy=True)
