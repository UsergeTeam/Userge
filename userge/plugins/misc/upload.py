import os
import time
from datetime import datetime
from pathlib import Path
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.errors.exceptions import FloodWait
from userge import userge, Config, Message
from userge.utils import progress, CANCEL_LIST, take_screen_shot

LOGGER = userge.getLogger(__name__)

LOGO_PATH = 'resources/userge(8).png'
THUMB_PATH = Config.DOWN_PATH + "thumb_image.jpg"


@userge.on_cmd("upload", about="""\
__upload files to telegram__

**Usage:**

    `.upload [file or folder path]`""")
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

        except FloodWait as x:
            time.sleep(x.x)  # asyncio sleep ?

    elif path.is_dir():
        for i in path.iterdir():
            await explorer(i, chatid)


async def upload(path: Path, chat_id: int):
    if path.name.endswith((".mkv", ".mp4", ".webm")):
        await vid_upload(chat_id, path)

    else:
        await doc_upload(chat_id, path)


async def doc_upload(chat_id, path):
    message: Message = await userge.send_message(chat_id, f"`Uploading {path.name} ...`")
    start_t = datetime.now()
    c_time = time.time()
    thumb = await get_thumb()
    await userge.send_chat_action(chat_id, "upload_document")
    the_real_download_location = await userge.send_document(
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
    await userge.send_chat_action(chat_id, "cancel")

    if message.message_id in CANCEL_LIST:
        CANCEL_LIST.remove(message.message_id)
        await message.edit("`Process Canceled!`", del_in=5)

    else:
        end_t = datetime.now()
        ms = (end_t - start_t).seconds
        await message.edit(f"Uploaded in {ms} seconds")


async def vid_upload(chat_id, path):
    strpath = str(path)
    thumb = await get_thumb(strpath)
    metadata = extractMetadata(createParser(strpath))

    message: Message = await userge.send_message(chat_id, f"`Uploading {path.name} ...` as a video")

    start_t = datetime.now()
    c_time = time.time()
    await userge.send_chat_action(chat_id, "upload_video")
    the_real_download_location = await userge.send_video(
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
    os.remove(thumb)

    if message.message_id in CANCEL_LIST:
        CANCEL_LIST.remove(message.message_id)
        await message.edit("`Process Canceled!`", del_in=5)

    else:
        end_t = datetime.now()
        ms = (end_t - start_t).seconds
        await message.edit(f"Uploaded in {ms} seconds")


async def get_thumb(path: str = '') -> str:
    if os.path.exists(THUMB_PATH):
        return THUMB_PATH

    if path:
        metadata = extractMetadata(createParser(path))

        if metadata and metadata.has("duration"):
            return await take_screen_shot(
                path, metadata.get("duration").seconds)

    return LOGO_PATH
