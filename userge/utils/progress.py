# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import time
from math import floor
from typing import Dict, Tuple, Optional

from pyrogram.errors.exceptions import FloodWait

import userge
from .tools import humanbytes, time_formatter
from .. import config

_TASKS: Dict[str, Tuple[float, float]] = {}


async def progress(current: int,
                   total: int,
                   message: 'userge.Message',
                   ud_type: str,
                   file_name: str = '',
                   delay: Optional[int] = None) -> None:
    """ progress function """
    if message.process_is_canceled:
        await message.client.stop_transmission()
    delay = delay or config.Dynamic.EDIT_SLEEP_TIMEOUT
    task_id = f"{message.chat.id}.{message.id}"
    if current == total:
        if task_id not in _TASKS:
            return
        del _TASKS[task_id]
        try:
            await message.edit("`finalizing process ...`")
        except FloodWait as f_e:
            time.sleep(f_e.value)
        return
    now = time.time()
    if task_id not in _TASKS:
        _TASKS[task_id] = (now, now)
    start, last = _TASKS[task_id]
    elapsed_time = now - start
    if (now - last) >= delay:
        _TASKS[task_id] = (start, now)
        percentage = current * 100 / total
        speed = current / elapsed_time
        time_to_completion = time_formatter(int((total - current) / speed))
        progress_str = \
            "__{}__ : `{}`\n" + \
            "```\n[{}{}]```\n" + \
            "**Progress** : `{}%`\n" + \
            "**Completed** : `{}`\n" + \
            "**Total** : `{}`\n" + \
            "**Speed** : `{}/s`\n" + \
            "**ETA** : `{}`"
        progress_str = progress_str.format(
            ud_type,
            file_name,
            ''.join((userge.config.FINISHED_PROGRESS_STR
                     for _ in range(floor(percentage / 5)))),
            ''.join((userge.config.UNFINISHED_PROGRESS_STR
                     for _ in range(20 - floor(percentage / 5)))),
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            time_to_completion if time_to_completion else "0 s")
        try:
            await message.edit(progress_str)
        except FloodWait as f_e:
            time.sleep(f_e.value)
