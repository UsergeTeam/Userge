""" downloader """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import re
import math
import asyncio
from typing import Tuple, Union
from datetime import datetime
from json import dumps
from urllib.parse import unquote_plus

from pySmartDL import SmartDL
from pyrogram.types import Message as PyroMessage

from userge import userge, Message, Config
from userge.utils import progress, humanbytes, extract_entities
from userge.utils.exceptions import ProcessCanceled

LOGGER = userge.getLogger(__name__)


@userge.on_cmd("download", about={
    'header': "Download files to server",
    'usage': "{tr}download [url | reply to telegram media]",
    'examples': "{tr}download https://speed.hetzner.de/100MB.bin | testing upload.bin"},
    check_downpath=True)
async def down_load_media(message: Message):
    """ download from tg and url """
    if message.reply_to_message:
        resource = message.reply_to_message
    elif message.input_str:
        resource = message.input_str
    else:
        await message.err("nothing found to download")
        return
    try:
        dl_loc, d_in = await handle_download(message, resource)
    except ProcessCanceled:
        await message.canceled()
    except Exception as e_e:  # pylint: disable=broad-except
        await message.err(str(e_e))
    else:
        await message.edit(f"Downloaded to `{dl_loc}` in {d_in} seconds")


async def handle_download(message: Message, resource: Union[Message, str],
                          from_url: bool = False) -> Tuple[str, int]:
    """ download from resource """
    if not isinstance(resource, PyroMessage):
        return await url_download(message, resource)
    if resource.media_group_id:
        resources = await message.client.get_media_group(
            resource.chat.id,
            resource.message_id
        )
        dlloc, din = [], 0
        for res in resources:
            dl_loc, d_in = await tg_download(message, res, from_url)
            din += d_in
            dlloc.append(dl_loc)
        return dumps(dlloc), din
    return await tg_download(message, resource)


async def url_download(message: Message, url: str) -> Tuple[str, int]:
    """ download from link """
    # pylint: disable=line-too-long
    pattern = r"^(?:(?:https|tg):\/\/)?(?:www\.)?(?:t\.me\/|openmessage\?)(?:(?:c\/(\d+))|(\w+)|(?:user_id\=(\d+)))(?:\/|&message_id\=)(\d+)(\?single)?$"
    # group 1: private supergroup id, group 2: chat username,
    # group 3: private group/chat id, group 4: message id
    # group 5: check for download single media from media group
    match = re.search(pattern, url.split('|', 1)[0].strip())
    if match:
        chat_id = None
        msg_id = int(match.group(4))
        if match.group(1):
            chat_id = int("-100" + match.group(1))
        elif match.group(2):
            chat_id = match.group(2)
        elif match.group(3):
            chat_id = int(match.group(3))
        if chat_id and msg_id:
            resource = await message.client.get_messages(chat_id, msg_id)
            if resource.media_group_id and not bool(match.group(5)):
                output = await handle_download(message, resource, True)
            elif resource.media:
                output = await tg_download(message, resource, True)
            else:
                raise Exception("given tg link doesn't have any media")
            return output
        raise Exception("invalid telegram message link!")
    await message.edit("`Downloading From URL...`")
    start_t = datetime.now()
    custom_file_name = unquote_plus(os.path.basename(url))
    if "|" in url:
        url, c_file_name = url.split("|", maxsplit=1)
        url = url.strip()
        if c_file_name:
            custom_file_name = c_file_name.strip()
    dl_loc = os.path.join(Config.DOWN_PATH, custom_file_name)
    downloader = SmartDL(url, dl_loc, progress_bar=False)
    downloader.start(blocking=False)
    with message.cancel_callback(downloader.stop):
        while not downloader.isFinished():
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
                         for _ in range(math.floor(percentage / 5)))),
                ''.join((Config.UNFINISHED_PROGRESS_STR
                         for _ in range(20 - math.floor(percentage / 5)))),
                round(percentage, 2),
                url,
                custom_file_name,
                humanbytes(downloaded),
                humanbytes(total_length),
                speed,
                estimated_total_time)
            await message.edit(progress_str, disable_web_page_preview=True)
            await asyncio.sleep(Config.EDIT_SLEEP_TIMEOUT)
    if message.process_is_canceled:
        raise ProcessCanceled
    return dl_loc, (datetime.now() - start_t).seconds


async def tg_download(
    message: Message, to_download: Message, from_url: bool = False
) -> Tuple[str, int]:
    """ download from tg file """
    if not to_download.media:
        dl_loc, mite = [], 0
        ets = extract_entities(to_download, ["url", "text_link"])
        if len(ets) == 0:
            raise Exception("nothing found to download")
        for uarl in ets:
            _dl_loc, b_ = await url_download(message, uarl)
            dl_loc.append(_dl_loc)
            mite += b_
        return dumps(dl_loc), mite
    await message.edit("`Downloading From TG...`")
    start_t = datetime.now()
    custom_file_name = Config.DOWN_PATH
    if message.filtered_input_str and not from_url:
        custom_file_name = os.path.join(Config.DOWN_PATH, message.filtered_input_str.strip())
    elif "|" in message.filtered_input_str:
        _, c_file_name = message.filtered_input_str.split("|", maxsplit=1)
        if c_file_name:
            custom_file_name = os.path.join(Config.DOWN_PATH, c_file_name.strip())
    with message.cancel_callback():
        dl_loc = await message.client.download_media(
            message=to_download,
            file_name=custom_file_name,
            progress=progress,
            progress_args=(message, "trying to download")
        )
    if message.process_is_canceled:
        raise ProcessCanceled
    if not isinstance(dl_loc, str):
        raise TypeError("File Corrupted!")
    dl_loc = os.path.relpath(dl_loc)
    return dl_loc, (datetime.now() - start_t).seconds
