# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import aiofiles

from userge import userge, Message


@userge.on_cmd("logs", about={'header': "check userge logs"})
async def check_logs(message: Message):
    """check logs"""
    await message.edit("`checking logs ...`")
    async with aiofiles.open("logs/userge.log", "r") as l_f:
        await message.edit_or_send_as_file(f"**USERGE LOGS** :\n\n`{await l_f.read()}`",
                                           filename='userge.log',
                                           caption='userge.log')
