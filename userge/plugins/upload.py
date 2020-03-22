import os
import time
import asyncio
from datetime import datetime
from pathlib import Path

from pyrogram import Message
from pyrogram.errors.exceptions import FloodWait

from userge import userge
from userge.utils import progress, take_screen_shot, extractMetadata, createParser

LOGGER = userge.getLogger(__name__)
thumb_image_path = 'resources/userge(8).png'


@userge.on_cmd("upload",
               about="upload files to telegram")
async def uploadtotg(_, message: Message):
    try:
        string = Path(message.text.split(" ", maxsplit=1)[1])

    except IndexError:
        await userge.send_err(message,
                              text="wrong syntax\n`.upload <path>`")

    else:
        await message.delete()
        await explorer(string, message.chat.id)


async def explorer(path: Path,
                   chatid: int):
    if path.is_file():
        try:
            await upload(path, chatid)
        except FloodWait as x:
            await asyncio.sleep(x.x + 5)
            await explorer(path, chatid)

    elif path.is_dir():
        for i in path.iterdir():
            await explorer(i, chatid)


async def upload(path: Path, chat_id: int):
    if path.name.endswith((".mkv", ".mp4", ".webm")):
        await vid_upload(chat_id, path)
    else:
        await doc_upload(chat_id, path)


async def doc_upload(chat_id, path):
    message = await userge.send_message(chat_id,
                                        text=f"`Uploading {path.name} ...`")
                                        
    start_t = datetime.now()
    c_time = time.time()

    await userge.send_document(chat_id=chat_id,
                               document=str(path),
                               thumb=thumb_image_path,
                               caption=path.name,
                               parse_mode="html",
                               disable_notification=True,
                               progress=progress,
                               progress_args=(
                                   "uploading", message, c_time))

    end_t = datetime.now()
    ms = (end_t - start_t).seconds
    await message.edit(f"Uploaded in {ms} seconds")


async def vid_upload(chat_id, path):
    strpath = str(path)
    metadata = extractMetadata(createParser(strpath))

    thumb = await take_screen_shot(strpath, metadata.get("duration").seconds) \
                if (metadata and metadata.has("duration")) else \
                    thumb_image_path

    message = await userge.send_message(chat_id,
                                        text=f"`Uploading {path.name} ...` as a video")

    start_t = datetime.now()
    c_time = time.time()

    await userge.send_video(chat_id=chat_id,
                            video=strpath,
                            thumb=thumb if thumb else thumb_image_path,
                            caption=path.name,
                            parse_mode="html",
                            disable_notification=True,
                            progress=progress,
                            progress_args=(
                                "uploading", message, time.time()))
                                
    os.remove(thumb)
    end_t = datetime.now()
    ms = (end_t - start_t).seconds

    await message.edit(f"Uploaded in {ms} seconds")
