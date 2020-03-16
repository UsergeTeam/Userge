from Userge import userge, logging, CMD_HELP

log = logging.getLogger(__name__)


from pyrogram import Filters, Message
from datetime import datetime


@userge.on_message(Filters.command("ping", ".") & Filters.me)
async def pingme(_, message: Message):
    start = datetime.now()
    await message.edit('`Pong!`')
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await message.edit(f"**Pong!**\n`{ms} ms`")


CMD_HELP.update({
    "ping": "check server speed :)"
})
