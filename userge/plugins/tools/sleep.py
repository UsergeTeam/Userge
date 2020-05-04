# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from time import sleep

from userge import userge, Message


@userge.on_cmd("sleep (\\d+)", about={
    'header': "sleep userge :P",
    'usage': "{tr}sleep [timeout in seconds]"})
async def sleep_(message: Message):
    seconds = int(message.matches[0].group(1))
    await message.edit(text=f"`sleeping {seconds} seconds...`")
    sleep(seconds)
    await message.delete()