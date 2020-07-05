# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import time
import math
import asyncio
from datetime import datetime
from urllib.parse import unquote_plus

from pySmartDL import SmartDL

from userge import userge, Message, Config
from userge.utils import progress, humanbytes

LOGGER = userge.getLogger(__name__)


@userge.on_cmd("download", about={
    'header': "Download files to server",
    'usage': "{tr}download [url | reply to telegram media]",
    'examples': "{tr}download https://speed.hetzner.de/100MB.bin | testing upload.bin"})
async def down_load_media(message: Message):
    await message.edit("Trying to Download...")
    if not os.path.isdir(Config.DOWN_PATH):
        os.mkdir(Config.DOWN_PATH)
    if message.reply_to_message and message.reply_to_message.media:
        start_t = datetime.now()
        c_time = time.time()
        dl_loc = await message.client.download_media(
            message=message.reply_to_message,
            file_name=Config.DOWN_PATH,
            progress=progress,
            progress_args=(
                "trying to download", userge, message, c_time
            )
        )
        if message.process_is_canceled:
            await message.edit("`Process Canceled!`", del_in=5)
        else:
            dl_loc = os.path.join(Config.DOWN_PATH, os.path.basename(dl_loc))
            end_t = datetime.now()
            m_s = (end_t - start_t).seconds
            await message.edit(f"Downloaded to `{dl_loc}` in {m_s} seconds")
    elif message.input_str:
        start_t = datetime.now()
        url = message.input_str
        custom_file_name = unquote_plus(os.path.basename(url))
        if "|" in url:
            url, custom_file_name = url.split("|")
            url = url.strip()
            custom_file_name = custom_file_name.strip()
        download_file_path = os.path.join(Config.DOWN_PATH, custom_file_name)
        try:
            downloader = SmartDL(url, download_file_path, progress_bar=False)
            downloader.start(blocking=False)
            count = 0
            while not downloader.isFinished():
                if message.process_is_canceled:
                    downloader.stop()
                    raise Exception('Process Canceled!')
                total_length = downloader.filesize if downloader.filesize else 0
                downloaded = downloader.get_dl_size()
                percentage = downloader.get_progress() * 100
                speed = downloader.get_speed(human=True)
                estimated_total_time = downloader.get_eta(human=True)
                progress_str = \
                    "__{}__\n" + \
                    "```[{}{}]```\n" + \
                    "**Progress** : `{}%`\n" + \
                    "**URL** : `{}`\n" + \
                    "**FILENAME** : `{}`\n" + \
                    "**Completed** : `{}`\n" + \
                    "**Total** : `{}`\n" + \
                    "**Speed** : `{}`\n" + \
                    "**ETA** : `{}`"
                progress_str = progress_str.format(
                    "trying to download",
                    ''.join((Config.FINISHED_PROGRESS_STR
                             for i in range(math.floor(percentage / 5)))),
                    ''.join((Config.UNFINISHED_PROGRESS_STR
                             for i in range(20 - math.floor(percentage / 5)))),
                    round(percentage, 2),
                    url,
                    custom_file_name,
                    humanbytes(downloaded),
                    humanbytes(total_length),
                    speed,
                    estimated_total_time)
                count += 1
                if count >= 5:
                    count = 0
                    await message.try_to_edit(progress_str, disable_web_page_preview=True)
                await asyncio.sleep(1)
        except Exception as e:
            await message.err(e)
        else:
            end_t = datetime.now()
            m_s = (end_t - start_t).seconds
            await message.edit(f"Downloaded to `{download_file_path}` in {m_s} seconds")
    else:
        await message.edit("Please read `.help download`", del_in=5)
