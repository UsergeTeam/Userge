# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import re
import math
import time
import asyncio
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote_plus

from pySmartDL import SmartDL
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.errors.exceptions import FloodWait

from userge import userge, Config, Message
from userge.utils import progress, take_screen_shot, humanbytes

LOGGER = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)

LOGO_PATH = 'resources/userge.png'
THUMB_PATH = Config.DOWN_PATH + "thumb_image.jpg"


@userge.on_cmd("rename", about={
    'header': "Rename telegram files",
    'flags': {'-d': "upload as document"},
    'usage': "{tr}rename [flags] [new_name_with_extention] : reply to telegram media",
    'examples': "{tr}rename -d test.mp4"}, del_pre=True)
async def rename_(message: Message):
    if not message.filtered_input_str:
        await message.err("new name not found!")
        return
    await message.edit("Trying to Rename...")
    if not os.path.isdir(Config.DOWN_PATH):
        os.mkdir(Config.DOWN_PATH)
    if message.reply_to_message and message.reply_to_message.media:
        c_time = time.time()
        dl_loc = await userge.download_media(
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
            await message.delete()
            dl_loc = os.path.join(Config.DOWN_PATH, os.path.basename(dl_loc))
            new_loc = os.path.join(Config.DOWN_PATH, message.filtered_input_str)
            os.rename(dl_loc, new_loc)
            await upload(Path(new_loc), message.chat.id, message.flags, True)
    else:
        await message.edit("Please read `.help rename`", del_in=5)


@userge.on_cmd("convert", about={
    'header': "Convert telegram files",
    'usage': "reply {tr}convert to any media"})
async def convert_(message: Message):
    await message.edit("Trying to Convert...")
    if not os.path.isdir(Config.DOWN_PATH):
        os.mkdir(Config.DOWN_PATH)
    if message.reply_to_message and message.reply_to_message.media:
        c_time = time.time()
        dl_loc = await userge.download_media(
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
            await message.delete()
            dl_loc = os.path.join(Config.DOWN_PATH, os.path.basename(dl_loc))
            flags = {} if message.reply_to_message.document else {'d': ''}
            await upload(Path(dl_loc), message.chat.id, flags, True)
    else:
        await message.edit("Please read `.help convert`", del_in=5)


@userge.on_cmd("upload", about={
    'header': "Upload files to telegram",
    'flags': {'-d': "upload as document"},
    'usage': "{tr}upload [flags] [file or folder path | link]",
    'examples': [
        "{tr}upload -d https://speed.hetzner.de/100MB.bin | test.bin",
        "{tr}upload downloads/test.mp4"]}, del_pre=True)
async def uploadtotg(message: Message):
    flags = message.flags
    path_ = message.filtered_input_str
    if not path_:
        await message.edit("invalid input!, check `.help .upload`", del_in=5)
        return
    is_url = re.search(r"(?:https?|ftp)://[^|\s]+\.[^|\s]+", path_)
    del_path = False
    if is_url:
        del_path = True
        await message.edit("`Downloading From URL...`")
        if not os.path.isdir(Config.DOWN_PATH):
            os.mkdir(Config.DOWN_PATH)
        url = is_url[0]
        file_name = unquote_plus(os.path.basename(url))
        if "|" in path_:
            file_name = path_.split("|")[1].strip()
        path_ = os.path.join(Config.DOWN_PATH, file_name)
        try:
            downloader = SmartDL(url, path_, progress_bar=False)
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
                    file_name,
                    humanbytes(downloaded),
                    humanbytes(total_length),
                    speed,
                    estimated_total_time)
                count += 1
                if count >= 5:
                    count = 0
                    await message.try_to_edit(progress_str, disable_web_page_preview=True)
                await asyncio.sleep(1)
        except Exception as d_e:
            await message.err(d_e)
            return
    if "|" in path_:
        path_, file_name = path_.split("|")
        path_ = path_.strip()
        if os.path.isfile(path_):
            new_path = os.path.join(Config.DOWN_PATH, file_name.strip())
            os.rename(path_, new_path)
            path_ = new_path
    try:
        string = Path(path_)
    except IndexError:
        await message.edit("wrong syntax\n`.upload [path]`")
    else:
        await message.delete()
        await explorer(string, message.chat.id, flags, del_path)


async def explorer(path: Path, chatid, flags, del_path):
    if path.is_file():
        try:
            if path.stat().st_size:
                await upload(path, chatid, flags, del_path)
        except FloodWait as x:
            time.sleep(x.x)  # asyncio sleep ?
    elif path.is_dir():
        for i in path.iterdir():
            await explorer(i, chatid, flags, del_path)


async def upload(path: Path, chat_id: int, flags: dict, del_path: bool = False):
    if path.name.endswith((".mkv", ".mp4", ".webm")) and ('d' not in flags):
        await vid_upload(chat_id, path, del_path)
    elif path.name.endswith((".mp3", ".flac", ".wav", ".m4a")) and ('d' not in flags):
        await audio_upload(chat_id, path, del_path)
    else:
        await doc_upload(chat_id, path, del_path)


async def doc_upload(chat_id, path, del_path: bool):
    message: Message = await userge.send_message(
        chat_id, f"`Uploading {path.name} ...`")
    start_t = datetime.now()
    c_time = time.time()
    thumb = await get_thumb()
    await userge.send_chat_action(chat_id, "upload_document")
    try:
        msg = await userge.send_document(
            chat_id=chat_id,
            document=str(path),
            thumb=thumb,
            caption=path.name,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(
                "uploading", userge, message, c_time, str(path.name)
            )
        )
    except Exception as u_e:
        await message.edit(u_e)
        raise u_e
    else:
        await finalize(chat_id, message, msg, start_t)
    finally:
        if os.path.exists(str(path)) and del_path:
            os.remove(str(path))


async def vid_upload(chat_id, path, del_path: bool):
    strpath = str(path)
    thumb = await get_thumb(strpath)
    metadata = extractMetadata(createParser(strpath))
    message: Message = await userge.send_message(
        chat_id, f"`Uploading {path.name} as a video ..`")
    start_t = datetime.now()
    c_time = time.time()
    await userge.send_chat_action(chat_id, "upload_video")
    try:
        msg = await userge.send_video(
            chat_id=chat_id,
            video=strpath,
            duration=metadata.get("duration").seconds,
            thumb=thumb,
            caption=path.name,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(
                "uploading", userge, message, c_time, str(path.name)
            )
        )
    except Exception as u_e:
        await message.edit(u_e)
        raise u_e
    else:
        await remove_thumb(thumb)
        await finalize(chat_id, message, msg, start_t)
    finally:
        if os.path.exists(str(path)) and del_path:
            os.remove(str(path))


async def audio_upload(chat_id, path, del_path: bool):
    title = None
    artist = None
    message: Message = await userge.send_message(
        chat_id, f"`Uploading {path.name} as audio ...`")
    strpath = str(path)
    start_t = datetime.now()
    c_time = time.time()
    thumb = await get_thumb()
    metadata = extractMetadata(createParser(strpath))
    if metadata.has("title"):
        title = metadata.get("title")
    if metadata.has("artist"):
        artist = metadata.get("artist")
    await userge.send_chat_action(chat_id, "upload_audio")
    try:
        msg = await userge.send_audio(
            chat_id=chat_id,
            audio=strpath,
            thumb=thumb,
            caption=path.name,
            title=title,
            performer=artist,
            duration=metadata.get("duration").seconds,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(
                "uploading", userge, message, c_time, str(path.name)
            )
        )
    except Exception as u_e:
        await message.edit(u_e)
        raise u_e
    else:
        await finalize(chat_id, message, msg, start_t)
    finally:
        if os.path.exists(str(path)) and del_path:
            os.remove(str(path))


async def get_thumb(path: str = ''):
    if os.path.exists(THUMB_PATH):
        return THUMB_PATH
    if path:
        metadata = extractMetadata(createParser(path))
        if metadata and metadata.has("duration"):
            return await take_screen_shot(
                path, metadata.get("duration").seconds)
    if os.path.exists(LOGO_PATH):
        return LOGO_PATH
    return None


async def remove_thumb(thumb: str) -> None:
    if (thumb and os.path.exists(thumb)
            and thumb != LOGO_PATH and thumb != THUMB_PATH):
        os.remove(thumb)


async def finalize(chat_id: int, message: Message, msg: Message, start_t):
    await CHANNEL.fwd_msg(msg)
    await userge.send_chat_action(chat_id, "cancel")
    if message.process_is_canceled:
        await message.edit("`Process Canceled!`", del_in=5)
    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(f"Uploaded in {m_s} seconds")
