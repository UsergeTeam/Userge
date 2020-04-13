# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import asyncio
from userge import userge, Message, Config

LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd('restart', about="""\
__Restarts the bot and reload all plugins__

**Usage:**

    `.restart` : normal restart.
    `.restart -h` : use this only if you are using heroku.""")
async def restart_cmd_handler(message: Message):
    await message.edit("Restarting Userge Services", log=True)
    LOG.info("USERGE Services - Restart initiated")

    if Config.HEROKU_APP and '-h' in message.flags:
        await message.edit(
            '`Heroku app found, trying to restart dyno...`', del_in=3)
        Config.HEROKU_APP.restart()

    else:
        asyncio.get_event_loop().create_task(restart(userge))
        await message.delete()


async def restart(client: userge):
    await client.restart()
    await CHANNEL.log("USERGE Services have been Restarted!")
    LOG.info("USERGE - Restarted")
