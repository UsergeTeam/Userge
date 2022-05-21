# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import io
import os
import time
from datetime import datetime
from pathlib import Path

import stagger
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.errors import FloodWait

from userge import userge, Message
from userge.utils import progress, take_screen_shot, humanbytes, sort_file_name_key
from .. import thumbnail

CHANNEL = userge.getCLogger(__name__)

LOGO_PATH = 'resources/userge.png'


async def upload_path(message: Message, path: Path, del_path: bool):
    file_paths = []
    if path.exists():
        def explorer(_path: Path) -> None:
            if _path.is_file() and _path.stat().st_size:
                file_paths.append(_path)
            elif _path.is_dir():
                for i in sorted(_path.iterdir(), key=lambda a: sort_file_name_key(a.name)):
                    explorer(i)
        explorer(path)
    else:
        path = path.expanduser()
        str_path = os.path.join(*(path.parts[1:] if path.is_absolute() else path.parts))
        for p in Path(path.root).glob(str_path):
            file_paths.append(p)
    current = 0
    for p_t in file_paths:
        current += 1
        try:
            await upload(message, p_t, del_path, f"{current}/{len(file_paths)}")
        except FloodWait as f_e:
            time.sleep(f_e.x)  # asyncio sleep ?
        if message.process_is_canceled:
            break


async def upload(message: Message, path: Path, del_path: bool = False,
                 extra: str = '', with_thumb: bool = True):
    if 'wt' in message.flags:
        with_thumb = False
    if 'r' in message.flags:
        del_path = True
    if path.name.lower().endswith(
            (".mkv", ".mp4", ".webm", ".m4v")) and ('d' not in message.flags):
        await vid_upload(message, path, del_path, extra, with_thumb)
    elif path.name.lower().endswith(
            (".mp3", ".flac", ".wav", ".m4a")) and ('d' not in message.flags):
        await audio_upload(message, path, del_path, extra, with_thumb)
    elif path.name.lower().endswith(
            (".jpg", ".jpeg", ".png", ".bmp")) and ('d' not in message.flags):
        await photo_upload(message, path, del_path, extra)
    else:
        await doc_upload(message, path, del_path, extra, with_thumb)


async def doc_upload(message: Message, path, del_path: bool = False,
                     extra: str = '', with_thumb: bool = True):
    str_path = str(path)
    sent: Message = await message.client.send_message(
        message.chat.id, f"`Uploading {str_path} as a doc ... {extra}`")
    start_t = datetime.now()
    thumb = await get_thumb(str_path) if with_thumb else None
    await message.client.send_chat_action(message.chat.id, "upload_document")
    try:
        msg = await message.client.send_document(
            chat_id=message.chat.id,
            document=str_path,
            thumb=thumb,
            caption=path.name,
            parse_mode="html",
            force_document=True,
            disable_notification=True,
            progress=progress,
            progress_args=(message, f"uploading {extra}", str_path)
        )
    except ValueError as e_e:
        await sent.edit(f"Skipping `{str_path}` due to {e_e}")
    except Exception as u_e:
        await sent.edit(str(u_e))
        raise u_e
    else:
        await sent.delete()
        await finalize(message, msg, start_t)
        if os.path.exists(str_path) and del_path:
            os.remove(str_path)


async def vid_upload(message: Message, path, del_path: bool = False,
                     extra: str = '', with_thumb: bool = True):
    str_path = str(path)
    thumb = await get_thumb(str_path) if with_thumb else None
    duration = 0
    metadata = extractMetadata(createParser(str_path))
    if metadata and metadata.has("duration"):
        duration = metadata.get("duration").seconds
    sent: Message = await message.client.send_message(
        message.chat.id, f"`Uploading {str_path} as a video ... {extra}`")
    start_t = datetime.now()
    await message.client.send_chat_action(message.chat.id, "upload_video")
    width = 0
    height = 0
    if thumb:
        t_m = extractMetadata(createParser(thumb))
        if t_m and t_m.has("width"):
            width = t_m.get("width")
        if t_m and t_m.has("height"):
            height = t_m.get("height")
    try:
        msg = await message.client.send_video(
            chat_id=message.chat.id,
            video=str_path,
            duration=duration,
            thumb=thumb,
            width=width,
            height=height,
            caption=path.name,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(message, f"uploading {extra}", str_path)
        )
    except ValueError as e_e:
        await sent.edit(f"Skipping `{str_path}` due to {e_e}")
    except Exception as u_e:
        await sent.edit(str(u_e))
        raise u_e
    else:
        await sent.delete()
        await remove_thumb(thumb)
        await finalize(message, msg, start_t)
        if os.path.exists(str_path) and del_path:
            os.remove(str_path)


async def audio_upload(message: Message, path, del_path: bool = False,
                       extra: str = '', with_thumb: bool = True):
    title = None
    artist = None
    thumb = None
    duration = 0
    str_path = str(path)
    file_size = humanbytes(os.stat(str_path).st_size)
    if with_thumb:
        try:
            album_art = stagger.read_tag(str_path)
            if album_art.picture and not os.path.lexists(thumbnail.Dynamic.THUMB_PATH):
                bytes_pic_data = album_art[stagger.id3.APIC][0].data
                bytes_io = io.BytesIO(bytes_pic_data)
                image_file = Image.open(bytes_io)
                image_file.save("album_cover.jpg", "JPEG")
                thumb = "album_cover.jpg"
        except stagger.errors.NoTagError:
            pass
        if not thumb:
            thumb = await get_thumb(str_path)
    metadata = extractMetadata(createParser(str_path))
    if metadata and metadata.has("title"):
        title = metadata.get("title")
    if metadata and metadata.has("artist"):
        artist = metadata.get("artist")
    if metadata and metadata.has("duration"):
        duration = metadata.get("duration").seconds
    sent: Message = await message.client.send_message(
        message.chat.id, f"`Uploading {str_path} as audio ... {extra}`")
    start_t = datetime.now()
    await message.client.send_chat_action(message.chat.id, "upload_audio")
    try:
        msg = await message.client.send_audio(
            chat_id=message.chat.id,
            audio=str_path,
            thumb=thumb,
            caption=f"{path.name}\n[ {file_size} ]",
            title=title,
            performer=artist,
            duration=duration,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(message, f"uploading {extra}", str_path)
        )
    except ValueError as e_e:
        await sent.edit(f"Skipping `{str_path}` due to {e_e}")
    except Exception as u_e:
        await sent.edit(str(u_e))
        raise u_e
    else:
        await sent.delete()
        await finalize(message, msg, start_t)
        if os.path.exists(str_path) and del_path:
            os.remove(str_path)
    finally:
        if os.path.lexists("album_cover.jpg"):
            os.remove("album_cover.jpg")


async def photo_upload(message: Message, path, del_path: bool = False, extra: str = ''):
    str_path = str(path)
    sent: Message = await message.client.send_message(
        message.chat.id, f"`Uploading {path.name} as photo ... {extra}`")
    start_t = datetime.now()
    await message.client.send_chat_action(message.chat.id, "upload_photo")
    try:
        msg = await message.client.send_photo(
            chat_id=message.chat.id,
            photo=str_path,
            caption=path.name,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(message, f"uploading {extra}", str_path)
        )
    except ValueError as e_e:
        await sent.edit(f"Skipping `{str_path}` due to {e_e}")
    except Exception as u_e:
        await sent.edit(str(u_e))
        raise u_e
    else:
        await sent.delete()
        await finalize(message, msg, start_t)
        if os.path.exists(str_path) and del_path:
            os.remove(str_path)


async def get_thumb(path: str = ''):
    if os.path.exists(thumbnail.Dynamic.THUMB_PATH):
        return thumbnail.Dynamic.THUMB_PATH
    if path:
        types = (".jpg", ".webp", ".png")
        if path.endswith(types):
            return None
        file_name = os.path.splitext(path)[0]
        for type_ in types:
            thumb_path = file_name + type_
            if os.path.exists(thumb_path):
                if type_ != ".jpg":
                    new_thumb_path = f"{file_name}.jpg"
                    Image.open(thumb_path).convert('RGB').save(new_thumb_path, "JPEG")
                    os.remove(thumb_path)
                    thumb_path = new_thumb_path
                return thumb_path
        metadata = extractMetadata(createParser(path))
        if metadata and metadata.has("duration"):
            return await take_screen_shot(
                path, metadata.get("duration").seconds)
    if os.path.exists(LOGO_PATH):
        return LOGO_PATH
    return None


async def remove_thumb(thumb: str) -> None:
    if (thumb and os.path.exists(thumb)
            and thumb != LOGO_PATH and thumb != thumbnail.Dynamic.THUMB_PATH):
        os.remove(thumb)


async def finalize(message: Message, msg: Message, start_t):
    if 'df' not in message.flags:
        await CHANNEL.fwd_msg(msg)
    await message.client.send_chat_action(message.chat.id, "cancel")
    if message.process_is_canceled:
        await message.canceled()
    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(f"Uploaded in {m_s} seconds", del_in=10)
