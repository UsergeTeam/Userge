from datetime import datetime
from userge import userge

log = userge.getLogger(__name__)


@userge.on_cmd("ping", about="check server speed :)")
async def pingme(_, message: userge.MSG):
    start = datetime.now()
    await message.edit('`Pong!`')
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await message.edit(f"**Pong!**\n`{ms} ms`")