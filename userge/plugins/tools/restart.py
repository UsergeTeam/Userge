# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import time
import asyncio
from userge import userge, Message, Config

LOG = userge.getLogger(__name__)


@userge.on_cmd('restart', about={
    'header': "Restarts the bot and reload all plugins",
    'flags': {'-h': "restart heroku dyno"},
    'usage': ".restart\n.restart -h"})
async def restart_cmd_handler(message: Message):
    if Config.PUSHING:
        await message.err("Can't Restart, Updation Found!")
        return

    await message.edit("Restarting Userge Services", log=__name__)
    LOG.info("USERGE Services - Restart initiated")

    if Config.HEROKU_APP and '-h' in message.flags:
        await message.edit(
            '`Heroku app found, trying to restart dyno...\nthis will take upto 30 sec`', del_in=3)
        Config.HEROKU_APP.restart()
        time.sleep(30)

    else:
        await message.edit("finalizing...", del_in=1)
        asyncio.get_event_loop().create_task(userge.restart())
