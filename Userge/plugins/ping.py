from datetime import datetime
from Userge import userge
from pyrogram import Filters, Message


@userge.on_message(Filters.command("ping", ".") & Filters.me)
def pingme(_, message: Message):
    start = datetime.now()
    message.edit('`Pong!`')
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    message.edit(f"**Pong!**\n`{ms} ms`")
