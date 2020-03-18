import time
from userge import userge
from pathlib import Path
from pyrogram import Message
from pyrogram.errors.exceptions import FloodWait

from userge.utils import (
    progress,
    take_screen_shot,
    extractMetadata,
    createParser
)

LOGGER = userge.getLogger(__name__)


@userge.on_cmd("upload", about="upload files to telegram")
async def uploadtotg(_, message):
    try:
        string = Path(message.text.split(" ", maxsplit=1)[1])

    except IndexError:
        await message.edit("wrong syntax\n`.upload <path>`")
    else:
        await message.delete()
        await explorer(string, message)


async def explorer(path: Path, message: Message):
    if path.is_file():
        try:
            await upload(path, message.chat.id)
        except FloodWait as x:
            time.sleep(x.x)  # asyncio sleep ?
            await message.edit(f"`Floodwait occured for {x.x} seconds")
    elif path.is_dir():
        for i in path.iterdir():
            await explorer(i, message)


async def upload(path: Path, chat_id: int):

    message = await userge.send_message(chat_id, "`Starting ...`")
    message_id = message.message_id
    size = path.stat().st_size
    if int(size) > (1024 * 1024 * 1500):
        await message.edit('<i>File Size Too Large(' + str(round(int(size) / (1024 * 1024), 0)) + 'MB)</i> \U0001f61e')
        return

    LOGGER.info(path.name)
    metadata = extractMetadata(createParser(str(path)))
    duration = 0
    width = 0
    height = 0
    title = None
    artist = None
    thumb = 'resources/userge(8).png'
    caption = path.name
    if metadata:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")
        if metadata.has("title"):
            title = metadata.get("title")
        if metadata.has("artist"):
            artist = metadata.get("artist")
    filename = str(path)
    if filename.endswith((".mkv", ".mp4", ".webm")) and duration:
        thumb = await take_screen_shot(f'./{filename}', duration)
    start_time = time.time()
    await message.edit('<i>Trying To Upload......</i> \U0001f9D0')
    try:
        if filename.endswith((".mp3", ".flac", ".wav", ".m4a")):
            await userge.send_audio(
                chat_id=chat_id,
                audio=filename,
                caption=caption,
                duration=duration,
                title=title,
                performer=artist,
                thumb=thumb,
                progress=progress,
                progress_args=(
                    userge,
                    message_id,
                    chat_id,
                    start_time,
                    '<i>Uploading......</i>\U0001f60E'
                )
            )
        elif filename.endswith((".mkv", ".mp4", ".webm")):
            await userge.send_video(
                chat_id=chat_id,
                video=filename,
                caption=caption,
                duration=duration,
                width=width,
                height=height,
                thumb=thumb,
                supports_streaming=True,
                progress=progress,
                progress_args=(
                    userge,
                    message_id,
                    chat_id,
                    start_time,
                    '<i>Uploading......</i>\U0001f60E'
                )
            )
        else:
            await userge.send_document(
                chat_id=chat_id,
                document=filename,
                thumb=thumb,
                caption=caption,
                progress=progress,
                progress_args=(
                    userge,
                    message_id,
                    chat_id,
                    start_time,
                    '<i>Uploading......</i>\U0001f60E'
                )
            )

            await userge.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='<i>Uploaded Successfully</i> \U0001f618'
            )
    except Exception as e:
        LOGGER.exception("Exception occurred")
        await userge.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"<b>ERROR:</b> <i>{e}</i>"
        )
