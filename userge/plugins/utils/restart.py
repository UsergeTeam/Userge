# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import asyncio
from userge import userge, Message

LOG = userge.getLogger(__name__)


@userge.on_cmd('restart', about="__Restarts the bot and reload all plugins__")
async def restart_cmd_handler(m: Message):
    await m.edit("Restarting Userge Services")
    LOG.info("USERGE Services - Restart initiated")
    asyncio.create_task(restart(userge, m))


async def restart(c: userge, m: Message):
    await c.restart()
    await m.edit("USERGE Services have been Restarted!")
    LOG.info("USERGE - Restarted")
