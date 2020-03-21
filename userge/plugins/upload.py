import time
from datetime import datetime
from userge.utils import progress
from userge import userge
from pathlib import Path
from pyrogram import Message
from pyrogram.errors.exceptions import FloodWait

LOGGER = userge.getLogger(__name__)


@userge.on_cmd("upload", about="upload files to telegram")
async def uploadtotg(_, message: Message):
    try:
        string = Path(message.text.split(" ", maxsplit=1)[1])

    except IndexError:
        await message.edit("wrong syntax\n`.upload <path>`")
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
    thumb_image_path = 'resources/userge(8).png'
    message = await userge.send_message(chat_id, f"`Uploading {path.name} ...`")
    start_t = datetime.now()
    c_time = time.time()
    doc_caption = path.name
    the_real_download_location = await userge.send_document(
        chat_id=chat_id,
        document=str(path),
        thumb=thumb_image_path,
        caption=doc_caption,
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
