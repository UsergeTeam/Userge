# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import userge, Message
from pyrogram.errors import MessageDeleteForbidden


@userge.on_cmd("del", about={'header': "delete replied message"})
async def del_msg(message: Message):
    try:
        if message.reply_to_message:
            await message.reply_to_message.delete()
        await message.delete()
    except MessageDeleteForbidden:
        pass
