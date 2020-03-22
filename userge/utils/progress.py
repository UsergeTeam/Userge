import math
import time
from .tools import humanbytes, time_formatter


async def progress(current,
                   total,
                   ud_type,
                   message,
                   start):
    now = time.time()
    diff = now - start

    if round(diff % 10.00) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = await time_formatter(milliseconds=elapsed_time)
        estimated_total_time = await time_formatter(milliseconds=estimated_total_time)

        progress = "[{0}{1}] \nP: {2}%\n".format(
            ''.join(["█" for i in range(math.floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))

        tmp = progress + "{0} of {1}\nSpeed: {2}/s\nETA: {3}\n".format(
            await humanbytes(current),
            await humanbytes(total),
            await humanbytes(speed),
            # elapsed_time if elapsed_time != '' else "0 s",
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        
        try:
            await message.edit("{}\n {}".format(ud_type, tmp))

        except:
            pass
