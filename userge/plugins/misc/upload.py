""" upload , rename and convert telegram files """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import io
import re
import math
import time
import asyncio
import stagger
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote_plus

from PIL import Image
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
    'examples': "{tr}rename -d test.mp4"}, del_pre=True, check_downpath=True)
async def rename_(message: Message):
    """ rename telegram files """
    if not message.filtered_input_str:
        await message.err("new name not found!")
        return
    await message.edit("`Trying to Rename ...`")
    if message.reply_to_message and message.reply_to_message.media:
        dl_loc = await message.client.download_media(
            message=message.reply_to_message,
            file_name=Config.DOWN_PATH,
            progress=progress,
            progress_args=(message, "trying to download")
        )
        if message.process_is_canceled:
            await message.edit("`Process Canceled!`", del_in=5)
        else:
            await message.delete()
            dl_loc = os.path.join(Config.DOWN_PATH, os.path.basename(dl_loc))
            new_loc = os.path.join(Config.DOWN_PATH, message.filtered_input_str)
            os.rename(dl_loc, new_loc)
            await upload(message, Path(new_loc), True)
    else:
        await message.edit("Please read `.help rename`", del_in=5)


@userge.on_cmd("convert", about={
    'header': "Convert telegram files",
    'usage': "reply {tr}convert to any media"}, del_pre=True, check_downpath=True)
async def convert_(message: Message):
    """ convert telegram files """
    await message.edit("`Trying to Convert ...`")
    if message.reply_to_message and message.reply_to_message.media:
        dl_loc = await message.client.download_media(
            message=message.reply_to_message,
            file_name=Config.DOWN_PATH,
            progress=progress,
            progress_args=(message, "trying to download")
        )
        if message.process_is_canceled:
            await message.edit("`Process Canceled!`", del_in=5)
        else:
            await message.delete()
            dl_loc = os.path.join(Config.DOWN_PATH, os.path.basename(dl_loc))
            message.text = '' if message.reply_to_message.document else ". -d"
            await upload(message, Path(dl_loc), True)
    else:
        await message.edit("Please read `.help convert`", del_in=5)


@userge.on_cmd("upload", about={
    'header': "Upload files to telegram",
    'flags': {'-d': "upload as document"},
    'usage': "{tr}upload [flags] [file or folder path | link]",
    'examples': [
        "{tr}upload -d https://speed.hetzner.de/100MB.bin | test.bin",
        "{tr}upload downloads/test.mp4"]}, del_pre=True, check_downpath=True)
async def uploadtotg(message: Message):
    """ upload to telegram """
    path_ = message.filtered_input_str
    if not path_:
        await message.edit("invalid input!, check `.help .upload`", del_in=5)
        return
    is_url = re.search(r"(?:https?|ftp)://[^|\s]+\.[^|\s]+", path_)
    del_path = False
    if is_url:
        del_path = True
        await message.edit("`Downloading From URL...`")
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
        await explorer(message, string, del_path)


async def explorer(message: Message, path: Path, del_path):
    if path.is_file():
        try:
            if path.stat().st_size:
                await upload(message, path, del_path)
        except FloodWait as x:
            time.sleep(x.x)  # asyncio sleep ?
    elif path.is_dir():
        for i in sorted(path.iterdir()):
            await explorer(message, i, del_path)


async def upload(message: Message, path: Path, del_path: bool = False):
    if path.name.endswith((".mkv", ".mp4", ".webm")) and ('d' not in message.flags):
        await vid_upload(message, path, del_path)
    elif path.name.endswith((".mp3", ".flac", ".wav", ".m4a")) and ('d' not in message.flags):
        await audio_upload(message, path, del_path)
    elif path.name.endswith((".jpg", ".jpeg", ".png", ".bmp")) and ('d' not in message.flags):
        await photo_upload(message, path, del_path)
    else:
        await doc_upload(message, path, del_path)


async def doc_upload(message: Message, path, del_path: bool):
    sent: Message = await message.client.send_message(
        message.chat.id, f"`Uploading {path.name} as a doc ...`")
    start_t = datetime.now()
    thumb = await get_thumb()
    await message.client.send_chat_action(message.chat.id, "upload_document")
    try:
        msg = await message.client.send_document(
            chat_id=message.chat.id,
            document=str(path),
            thumb=thumb,
            caption=path.name,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(message, "uploading", str(path.name))
        )
    except Exception as u_e:
        await sent.edit(u_e)
        raise u_e
    else:
        await sent.delete()
        await finalize(message, msg, start_t)
    finally:
        if os.path.exists(str(path)) and del_path:
            os.remove(str(path))


async def vid_upload(message: Message, path, del_path: bool):
    strpath = str(path)
    thumb = await get_thumb(strpath)
    duration = 0
    metadata = extractMetadata(createParser(strpath))
    if metadata and metadata.has("duration"):
        duration = metadata.get("duration").seconds
    sent: Message = await message.client.send_message(
        message.chat.id, f"`Uploading {path.name} as a video ..`")
    start_t = datetime.now()
    await message.client.send_chat_action(message.chat.id, "upload_video")
    try:
        msg = await message.client.send_video(
            chat_id=message.chat.id,
            video=strpath,
            duration=duration,
            thumb=thumb,
            caption=path.name,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(message, "uploading", str(path.name))
        )
    except Exception as u_e:
        await sent.edit(u_e)
        raise u_e
    else:
        await sent.delete()
        await remove_thumb(thumb)
        await finalize(message, msg, start_t)
    finally:
        if os.path.exists(str(path)) and del_path:
            os.remove(str(path))


async def audio_upload(message: Message, path, del_path: bool):
    title = None
    artist = None
    thumb = None
    duration = 0
    strpath = str(path)
    file_size = humanbytes(os.stat(strpath).st_size)
    try:
        album_art = stagger.read_tag(strpath)
        if (album_art.picture and not os.path.lexists(THUMB_PATH)):
            bytes_pic_data = album_art[stagger.id3.APIC][0].data
            bytes_io = io.BytesIO(bytes_pic_data)
            image_file = Image.open(bytes_io)
            image_file.save("album_cover.jpg", "JPEG")
            thumb = "album_cover.jpg"
    except stagger.errors.NoTagError:
        pass
    metadata = extractMetadata(createParser(strpath))
    if metadata and metadata.has("title"):
        title = metadata.get("title")
    if metadata and metadata.has("artist"):
        artist = metadata.get("artist")
    if metadata and metadata.has("duration"):
        duration = metadata.get("duration").seconds
    sent: Message = await message.client.send_message(
        message.chat.id, f"`Uploading {path.name} as audio ...`")
    start_t = datetime.now()
    await message.client.send_chat_action(message.chat.id, "upload_audio")
    try:
        msg = await message.client.send_audio(
            chat_id=message.chat.id,
            audio=strpath,
            thumb=thumb,
            caption=f"{path.name} [ {file_size} ]",
            title=title,
            performer=artist,
            duration=duration,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(message, "uploading", str(path.name))
        )
    except Exception as u_e:
        await sent.edit(u_e)
        raise u_e
    else:
        await sent.delete()
        await finalize(message, msg, start_t)
    finally:
        if os.path.lexists("album_cover.jpg"):
            os.remove("album_cover.jpg")
        if os.path.exists(str(path)) and del_path:
            os.remove(str(path))


async def photo_upload(message: Message, path, del_path: bool):
    strpath = str(path)
    sent: Message = await message.client.send_message(
        message.chat.id, f"`Uploading {path.name} as photo ...`")
    start_t = datetime.now()
    await message.client.send_chat_action(message.chat.id, "upload_photo")
    try:
        msg = await message.client.send_photo(
            chat_id=message.chat.id,
            photo=strpath,
            caption=path.name,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(message, "uploading", str(path.name))
        )
    except Exception as u_e:
        await sent.edit(u_e)
        raise u_e
    else:
        await sent.delete()
        await finalize(message, msg, start_t)
    finally:
        if os.path.exists(strpath) and del_path:
            os.remove(strpath)


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


async def finalize(message: Message, msg: Message, start_t):
    await CHANNEL.fwd_msg(msg)
    await message.client.send_chat_action(message.chat.id, "cancel")
    if message.process_is_canceled:
        await message.edit("`Process Canceled!`", del_in=5)
    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(f"Uploaded in {m_s} seconds", del_in=10)
