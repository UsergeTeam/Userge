import asyncio
from userge import userge, Message

LOG = userge.getLogger(__name__)


@userge.on_cmd('restart', about="__Restarts the bot and load all plugins__")
async def restart_cmd_handler(m: Message):
    await m.reply("Restarting Userge Services")
    LOG.info(f"USERGE Services - Restart initiated")
    asyncio.create_task(restart(userge, m))


async def restart(c: userge, m: Message):
    await c.restart()
    await m.edit(f"USERGE Services have been Restarted!")
    LOG.info(f"USERGE - Restarted")
