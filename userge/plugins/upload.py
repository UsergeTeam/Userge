import os
import time
from datetime import datetime
from pathlib import Path
from pyrogram.errors.exceptions import FloodWait
from userge import userge, Message
from userge.utils import progress, take_screen_shot, extractMetadata, createParser

LOGGER = userge.getLogger(__name__)
thumb_image_path = 'resources/userge(8).png'


@userge.on_cmd("upload", about="__upload files to telegram__")
async def uploadtotg(message: Message):
    try:
        string = Path(message.input_str)

    except IndexError:
        await message.edit("wrong syntax\n`.upload [path]`")

    else:
        await message.delete()
        await explorer(string, message.chat.id)


async def explorer(path: Path, chatid):
    if path.is_file():
        try:
            await upload(path, chatid)
            await userge.send_chat_action(chatid, "cancel")

        except FloodWait as x:
            time.sleep(x.x)  # asyncio sleep ?

    elif path.is_dir():
        for i in path.iterdir():
            await explorer(i, chatid)


async def upload(path: Path, chat_id: int):
    if path.name.endswith((".mkv", ".mp4", ".webm")):
        await userge.send_chat_action(chat_id, "upload_video")
        await vid_upload(chat_id, path)

    else:
        await userge.send_chat_action(chat_id, "upload_document")
        await doc_upload(chat_id, path)


async def doc_upload(chat_id, path):
    message: Message = await userge.send_message(chat_id, f"`Uploading {path.name} ...`")
    start_t = datetime.now()
    c_time = time.time()

    the_real_download_location = await userge.send_document(
        chat_id=chat_id,
        document=str(path),
        thumb=thumb_image_path,
        caption=path.name,
        parse_mode="html",
        disable_notification=True,
        progress=progress,
        progress_args=(
            "uploading", message, c_time
        )
    )

    end_t = datetime.now()
    ms = (end_t - start_t).seconds
    await message.edit(f"Uploaded in {ms} seconds")


async def vid_upload(chat_id, path):
    strpath = str(path)
    metadata = extractMetadata(createParser(strpath))
    thumb = await take_screen_shot(strpath, metadata.get("duration").seconds) \
        if (metadata and metadata.has("duration")) \
            else thumb_image_path

    message: Message = await userge.send_message(chat_id, f"`Uploading {path.name} ...` as a video")

    start_t = datetime.now()
    c_time = time.time()

    the_real_download_location = await userge.send_video(
        chat_id=chat_id,
        video=strpath,
        duration=metadata.get("duration").seconds,
        thumb=thumb if thumb else thumb_image_path,
        caption=path.name,
        parse_mode="html",
        disable_notification=True,
        progress=progress,
        progress_args=(
            "uploading", message, c_time
        )
    )
    
    os.remove(thumb)
    end_t = datetime.now()
    ms = (end_t - start_t).seconds
    await message.edit(f"Uploaded in {ms} seconds")
