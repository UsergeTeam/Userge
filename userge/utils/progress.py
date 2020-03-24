from pyrogram import Message
from pyrogram.errors.exceptions import FloodWait
import time


async def progress(
        current,
        total,
        ud_type,
        message: Message,
        start
):
    now = time.time()
    diff = now - start
    if diff % 10 < 0.1 or current == total:
        percentage = current * 100 // total
        speed = current // diff
        time_to_completion = (total - current) // speed
        time_to_completion = time_formatter(seconds=time_to_completion)
        progress_str = "Progress :: {}%\n".format(int(percentage))
        out = progress_str + "{0} of {1}\nSpeed: {2}/s\nETA: {3}\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            time_to_completion if time_to_completion != '' else "0 s"
        )
        text = "{}\n{}".format(
            ud_type,
            out
        )
        if message.text != text:
            try:
                await message.edit(text)
            except FloodWait:
                pass


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 1024
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return "{:.2f} {}B".format(size, Dic_powerN[n])


def time_formatter(seconds: int) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s, ") if seconds else "")
    return tmp[:-2]
