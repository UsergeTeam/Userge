from userge import userge
import asyncio
from pyrogram import Message
LOG = userge.getLogger(__name__)


@userge.on_cmd('restart', about="Restarts the bot and reload all plugins")
async def restart_cmd_handler(client: userge, m: Message):
    ack_message = await m.reply(
        text=f"Restarting Userge Services",
        reply_to_message_id=m.message_id
    )
    LOG.info(f"USERGE Services - Restart initiated")
    asyncio.get_event_loop().create_task(restart(client, ack_message))


async def restart(c, m):
    await c.restart()
    await m.edit_text(f"USERGE Services have been Restarted!")
    LOG.info(f"USERGE - Restarted")
