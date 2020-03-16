from pyrogram import Message
from datetime import datetime
from userge import userge

log = userge.getLogger(__name__)


@userge.on_cmd("ping")
async def pingme(_, message: Message):
    start = datetime.now()
    await message.edit('`Pong!`')
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await message.edit(f"**Pong!**\n`{ms} ms`")


userge.add_help(
    command="ping",
    about="check server speed :)"
)