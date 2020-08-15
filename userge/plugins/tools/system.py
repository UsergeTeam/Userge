""" system commands """
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import sys
import time
import asyncio
import shutil

from userge import userge, Message, Config

LOG = userge.getLogger(__name__)


@userge.on_cmd('restart', about={
    'header': "Restarts the bot and reload all plugins",
    'flags': {
        '-h': "restart heroku dyno",
        '-t': "clean temp loaded plugins",
        '-d': "clean working folder"},
    'usage': "{tr}restart [flag | flags]",
    'examples': "{tr}restart -t -d"}, del_pre=True, allow_channels=False)
async def restart_(message: Message):
    await message.edit("Restarting Userge Services", log=__name__)
    LOG.info("USERGE Services - Restart initiated")
    if 't' in message.flags:
        shutil.rmtree(Config.TMP_PATH, ignore_errors=True)
    if 'd' in message.flags:
        shutil.rmtree(Config.DOWN_PATH, ignore_errors=True)
    if Config.HEROKU_APP and 'h' in message.flags:
        await message.edit(
            '`Heroku app found, trying to restart dyno...\nthis will take upto 30 sec`', del_in=3)
        Config.HEROKU_APP.restart()
        time.sleep(30)
    else:
        await message.edit("finalizing...", del_in=1)
        asyncio.get_event_loop().create_task(userge.restart())


@userge.on_cmd("shutdown", about={'header': "shutdown userge :)"}, allow_channels=False)
async def shutdown_(message: Message) -> None:
    await message.edit("`shutting down ...`")
    if Config.HEROKU_APP:
        try:
            Config.HEROKU_APP.scale_formation_process("worker", 0)
        except Exception as h_e:  # pylint: disable=broad-except
            await message.err(h_e)
    else:
        await asyncio.sleep(1)
    await message.delete()
    sys.exit()


@userge.on_cmd("sleep (\\d+)", about={
    'header': "sleep userge :P",
    'usage': "{tr}sleep [timeout in seconds]"}, allow_channels=False)
async def sleep_(message: Message) -> None:
    seconds = int(message.matches[0].group(1))
    await message.edit(f"`sleeping {seconds} seconds...`")
    asyncio.get_event_loop().create_task(_slp_wrkr(seconds))


async def _slp_wrkr(seconds: int) -> None:
    await userge.stop()
    await asyncio.sleep(seconds)
    await userge.reload_plugins()
    await userge.start()
