import time
from pyrogram import Client, Message
from pyrogram.errors.exceptions import FloodWait
from .tools import humanbytes, time_formatter

CANCEL_LIST = []


async def progress(current: int,
                   total: int,
                   ud_type: str,
                   userge: Client,
                   message: Message,
                   start: int) -> None:
    if message.message_id in CANCEL_LIST:
        await userge.stop_transmission()

    now = time.time()
    diff = now - start
    if diff % 10 < 0.1 or current == total:
        percentage = current * 100 // total
        speed = current // diff
        time_to_completion = (total - current) // speed
        time_to_completion = time_formatter(seconds=int(time_to_completion))
        progress_str = "Progress :: {}%\n".format(int(percentage))

        out = progress_str + "{0}\n{1} of {2}\nSpeed: {3}/s\nETA: {4}\n".format(
            ud_type,
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            time_to_completion if time_to_completion != '' else "0 s"
        )

        if message.text != out:
            try:
                await message.edit(out)
            except FloodWait:
                pass
