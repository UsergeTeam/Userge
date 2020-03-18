import time
import math
import asyncio
from .tools import humanbytes, TimeFormatter


async def progress(current, total, client, message_id, chat_id, start, status):
    now = time.time()
    diff = now - start

    if current == total or round(diff % 15) == 0:
        percentage = current * 100 / total
        speed = current / diff

        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        time_to_completion = await TimeFormatter(milliseconds=time_to_completion)
        estimated_total_time = await TimeFormatter(milliseconds=estimated_total_time)

        progress = "<code>{}{}</code>\n<i>{}%</i>  |  <i>{}ps\n{}</i>  |  <i>{}</i>\n<b>Total:</b> <i>{}</i>\n<b>Rem:</b> <i>{}</i>".format(
            ''.join(["█" for i in range(math.floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2),
            await humanbytes(speed),
            await humanbytes(current),
            await humanbytes(total),
            estimated_total_time if estimated_total_time != '' else "0s",
            time_to_completion if time_to_completion != '' else "0s"
        )

        try:
            if current == total:
                await client.edit_message_text(
                    chat_id,
                    message_id,
                    text="<i>Completing Process...</i>\n<b>Please Wait !</b>"
                )

                await asyncio.sleep(1)

            await client.edit_message_text(
                chat_id,
                message_id,
                text="{}\n{}".format(
                    status,
                    progress
                )
            )

        except Exception:
            pass