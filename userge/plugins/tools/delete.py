# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram.errors import MessageDeleteForbidden

from userge import userge, Message


@userge.on_cmd("del", about={'header': "delete replied message"})
async def del_msg(message: Message):
    if userge.dual_mode:
        u_msg_ids = []
        b_msg_ids = []
        o_msg_ids = []
        for m in filter(lambda _: _, (message, message.reply_to_message)):
            if m.from_user and m.from_user.id == userge.id:
                u_msg_ids.append(m.message_id)
            elif m.from_user and m.from_user.id == userge.bot.id:
                b_msg_ids.append(m.message_id)
            else:
                o_msg_ids.append(m.message_id)
        if u_msg_ids:
            await userge.delete_messages(message.chat.id, u_msg_ids)
        if b_msg_ids:
            await userge.bot.delete_messages(message.chat.id, b_msg_ids)
        for o_msg_id in o_msg_ids:
            try:
                await userge.delete_messages(message.chat.id, o_msg_id)
            except MessageDeleteForbidden:
                try:
                    await userge.bot.delete_messages(message.chat.id, o_msg_id)
                except MessageDeleteForbidden:
                    pass
    else:
        await message.delete()
        replied = message.reply_to_message
        if replied:
            await replied.delete()
