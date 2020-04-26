# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import os
import time
from datetime import datetime
from pathlib import Path
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.errors.exceptions import FloodWait
from userge import userge, Config, Message
from userge.utils import progress, take_screen_shot

LOGGER = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)

LOGO_PATH = 'resources/userge.png'
THUMB_PATH = Config.DOWN_PATH + "thumb_image.jpg"


@userge.on_cmd("upload", about={
    'header': "Upload files to telegram",
    'flags': {'-d': "upload as document"},
    'usage': ".upload [flags] [file or folder path]"}, del_pre=True)
async def uploadtotg(message: Message):
    flags = message.flags
    path_ = message.filtered_input_str
    if not path_:
        await message.edit("invalid input!, check `.help .upload`", del_in=5)
        return

    try:
        string = Path(path_)

    except IndexError:
        await message.edit("wrong syntax\n`.upload [path]`")

    else:
        await message.delete()
        await explorer(string, message.chat.id, flags)


async def explorer(path: Path, chatid, flags):
    if path.is_file():
        try:
            await upload(path, chatid, flags)

        except FloodWait as x:
            time.sleep(x.x)  # asyncio sleep ?

    elif path.is_dir():
        for i in path.iterdir():
            await explorer(i, chatid, flags)


async def upload(path: Path, chat_id: int, flags):
    if path.name.endswith((".mkv", ".mp4", ".webm")) and ('d' not in flags):
        await vid_upload(chat_id, path)
    elif path.name.endswith((".mp3", ".flac", ".wav", ".m4a")) and ('d' not in flags):
        await audio_upload(chat_id, path)
    else:
        await doc_upload(chat_id, path)


async def doc_upload(chat_id, path):
    message: Message = await userge.send_message(
        chat_id, f"`Uploading {path.name} ...`")

    start_t = datetime.now()
    c_time = time.time()
    thumb = await get_thumb()
    await userge.send_chat_action(chat_id, "upload_document")
    msg = await userge.send_document(
        chat_id=chat_id,
        document=str(path),
        thumb=thumb,
        caption=path.name,
        parse_mode="html",
        disable_notification=True,
        progress=progress,
        progress_args=(
            "uploading", userge, message, c_time
        )
    )

    await finalize(chat_id, message, msg, start_t)


async def finalize(chat_id, message, msg, start_t):
    await CHANNEL.fwd_msg(msg)
    await userge.send_chat_action(chat_id, "cancel")
    if message.process_is_canceled:
        await message.edit("`Process Canceled!`", del_in=5)

    else:
        end_t = datetime.now()
        ms = (end_t - start_t).seconds
        await message.edit(f"Uploaded in {ms} seconds")


async def vid_upload(chat_id, path):
    strpath = str(path)
    thumb = await get_thumb(strpath)
    metadata = extractMetadata(createParser(strpath))

    message: Message = await userge.send_message(
        chat_id, f"`Uploading {path.name} as a video ..`")

    start_t = datetime.now()
    c_time = time.time()
    await userge.send_chat_action(chat_id, "upload_video")
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
            "uploading", userge, message, c_time
        )
    )
    await userge.send_chat_action(chat_id, "cancel")
    await CHANNEL.fwd_msg(msg)
    await remove_thumb(thumb)

    if message.process_is_canceled:
        await message.edit("`Process Canceled!`", del_in=5)

    else:
        end_t = datetime.now()
        ms = (end_t - start_t).seconds
        await message.edit(f"Uploaded in {ms} seconds")


async def audio_upload(chat_id, path):
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
            "uploading", userge, message, c_time
        )
    )

    await finalize(chat_id, message, msg, start_t)


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
    if os.path.exists(thumb) and \
            thumb != LOGO_PATH and \
            thumb != THUMB_PATH:
        os.remove(thumb)
