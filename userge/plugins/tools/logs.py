# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import aiofiles

from userge import userge, Message, logging


@userge.on_cmd("logs", about={'header': "check userge logs"}, allow_channels=False)
async def check_logs(message: Message):
    """ check logs """
    await message.edit("`checking logs ...`")
    async with aiofiles.open("logs/userge.log", "r") as l_f:
        await message.edit_or_send_as_file(f"**USERGE LOGS** :\n\n`{await l_f.read()}`",
                                           filename='userge.log',
                                           caption='userge.log')

_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


@userge.on_cmd("setlvl", about={
    'header': "set logger level, default to info",
    'types': ['debug', 'info', 'warning', 'error', 'critical'],
    'usage': "{tr}setlvl [level]",
    'examples': ["{tr}setlvl info", "{tr}setlvl debug"]})
async def set_level(message: Message):
    """ set logger level """
    await message.edit("`setting logger level ...`")
    level = message.input_str.lower()
    if level not in _LEVELS:
        await message.err("unknown level !")
        return
    for logger in (logging.getLogger(name) for name in logging.root.manager.loggerDict):
        logger.setLevel(_LEVELS[level])
    await message.edit(f"`successfully set logger level as **{level.upper()}**`", del_in=3)
