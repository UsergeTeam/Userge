# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import time
from pyrogram.errors.exceptions import FloodWait

from userge.core._userge.base import BaseClient, BaseMessage
from .tools import humanbytes, time_formatter


async def progress(current: int,
                   total: int,
                   ud_type: str,
                   userge: BaseClient,
                   message: BaseMessage,
                   start: int) -> None:

    if message.process_is_canceled:
        await userge.stop_transmission()

    now = time.time()
    diff = now - start

    if diff % 10 < 0.5 or current == total:
        percentage = current * 100 // total
        speed = current // diff
        time_to_completion = (total - current) // speed
        time_to_completion = time_formatter(seconds=int(time_to_completion))
        progress_str = "Progress :: {}%\n".format(int(percentage))

        out = progress_str + "{0}\n{1} of {2}\nSpeed: {3}/s\nETA: {4}\n".format(
            ud_type,
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            time_to_completion if time_to_completion != '' else "0 s"
        )

        if message.text != out:
            try:
                await message.edit(out)
            except FloodWait:
                pass
