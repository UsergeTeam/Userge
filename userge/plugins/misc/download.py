# Copyright (C) 2020 by UsergeTeam@Telegram, < https://t.me/theUserge >.
#
# This file is part of < https://github.com/uaudith/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import asyncio
import math
import os
import time
from datetime import datetime
from pySmartDL import SmartDL
from userge import userge, Message, Config
from userge.utils import progress, humanbytes

LOGGER = userge.getLogger(__name__)


@userge.on_cmd("download", about="""\
__download files to server__

**Usage:**

    `.download [url | reply to telegram media]`

**Example:**

    `.download https://speed.hetzner.de/100MB.bin | testing upload.bin`""")
async def down_load_media(message: Message):
    await message.edit("Trying to Download...")
    if message.reply_to_message is not None:
        start_t = datetime.now()
        c_time = time.time()

        the_real_download_location = await userge.download_media(
            message=message.reply_to_message,
            file_name=Config.DOWN_PATH,
            progress=progress,
            progress_args=(
                "trying to download", userge, message, c_time
            )
        )
        # await userge.send_chat_action(message.chat.id, "cancel")

        if message.process_is_canceled:
            await message.edit("`Process Canceled!`", del_in=5)

        else:
            end_t = datetime.now()
            ms = (end_t - start_t).seconds
            await message.edit(
                f"Downloaded to `{the_real_download_location}` in {ms} seconds")

    elif message.input_str:
        start_t = datetime.now()
        url = message.input_str
        custom_file_name = os.path.basename(url)

        if "|" in url:
            url, custom_file_name = url.split("|")
            url = url.strip()
            custom_file_name = custom_file_name.strip()

        download_file_path = os.path.join(Config.DOWN_PATH, custom_file_name)
        downloader = SmartDL(url, download_file_path, progress_bar=False)
        downloader.start(blocking=False)
        c_time = time.time()

        while not downloader.isFinished():
            total_length = downloader.filesize if downloader.filesize else None
            downloaded = downloader.get_dl_size()
            display_message = ""
            now = time.time()
            diff = now - c_time
            percentage = downloader.get_progress() * 100
            # speed = downloader.get_speed()
            # elapsed_time = round(diff) * 1000

            progress_str = "[{0}{1}]\nProgress: {2}%".format(
                ''.join(["█" for i in range(math.floor(percentage / 5))]),
                ''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2))
            estimated_total_time = downloader.get_eta(human=True)

            try:
                current_message = f"trying to download\n"
                current_message += f"URL: {url}\n"
                current_message += f"File Name: {custom_file_name}\n"
                current_message += f"{progress_str}\n"
                current_message += f"{humanbytes(downloaded)} of {humanbytes(total_length)}\n"
                current_message += f"ETA: {estimated_total_time}"

                if round(diff % 10.00) == 0 and current_message != display_message:
                    await message.edit(text=current_message,
                                       disable_web_page_preview=True)

                    # display_message = current_message
                    await asyncio.sleep(10)

            except Exception as e:
                LOGGER.info(e)

        if os.path.exists(download_file_path):
            end_t = datetime.now()
            ms = (end_t - start_t).seconds

            await message.edit(f"Downloaded to `{download_file_path}` in {ms} seconds")

    else:
        await message.edit(
            "Reply to a Telegram Media, to download it to local server.", del_in=3)
