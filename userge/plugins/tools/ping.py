from datetime import datetime
from userge import userge, Message


@userge.on_cmd("ping", about="__check how long it takes to ping your userbot__")
async def pingme(message: Message):
    start = datetime.now()

    await message.edit('`Pong!`')

    end = datetime.now()
    ms = (end - start).microseconds / 1000

    await message.edit(f"**Pong!**\n`{ms} ms`")
