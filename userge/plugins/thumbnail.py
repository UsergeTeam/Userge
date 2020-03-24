import os
import time
from datetime import datetime
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from userge import userge, Config, Message
from userge.utils import progress

THUMB_PATH = Config.DOWN_PATH + "thumb_image.jpg"


@userge.on_cmd('sthumb', about="__Save thumbnail__")
async def save_thumb_nail(message: Message):
    await message.edit("processing ...")
    if message.reply_to_message is not None:
        start_t = datetime.now()
        c_time = time.time()

        downloaded_file_name = await userge.download_media(
                    message=message.reply_to_message,
                    file_name=Config.DOWN_PATH,
                    progress=progress,
                    progress_args=(
                        "trying to download", message, c_time))

        Image.open(downloaded_file_name).convert("RGB").save(downloaded_file_name)
        metadata = extractMetadata(createParser(downloaded_file_name))
        height = 0
        if metadata and metadata.has("height"):
            height = metadata.get("height")
        img = Image.open(downloaded_file_name)
        img.resize((320, height or 320))
        img.save(THUMB_PATH, "JPEG")
        os.remove(downloaded_file_name)
        end_t = datetime.now()
        ms = (end_t - start_t).seconds

        await message.edit(f"thumbnail saved in {ms} seconds.", del_in=3)
    else:
        await message.edit("Reply to a photo to save custom thumbnail", del_in=3)


@userge.on_cmd('dthumb', about="__Delete thumbnail__")
async def clear_thumb_nail(message: Message):
    await message.edit("processing ...")
    if os.path.exists(THUMB_PATH):
        os.remove(THUMB_PATH)

    await message.edit("✅ Custom thumbnail deleted succesfully.", del_in=3)


@userge.on_cmd('vthumb', about="__View thumbnail__")
async def get_thumb_nail(message: Message):
    await message.edit("processing ...")
    if message.reply_to_message is not None:
        """reply_to_message = message.reply_to_message
        thumb_image_file_id = None
        file_di_ref = None
        if reply_to_message.document is not None:
            thumb_image_file_id = reply_to_message.document.thumbs[0].file_id
            file_di_ref = reply_to_message.document.file_ref
        if reply_to_message.video is not None:
            thumb_image_file_id = reply_to_message.video.thumbs[0].file_id
            file_di_ref = reply_to_message.video.file_ref
        if thumb_image_file_id is not None:
            print(thumb_image_file_id)
            print(file_di_ref)
            download_location = TMP_DOWNLOAD_DIRECTORY + "/"
            c_time = time.time()
            downloaded_file_name = await client.download_media(
                message=thumb_image_file_id,
                file_ref=file_di_ref,
                file_name=download_location,
                progress=progress_for_pyrogram,
                progress_args=(
                    "trying to download", message, c_time
                )
            )
            print(downloaded_file_name)
            await client.send_document(
                chat_id=message.chat.id,
                document=downloaded_file_name,
                disable_notification=True,
                reply_to_message_id=message.message_id
            )
            os.remove(downloaded_file_name)
        await message.delete()"""
        
        await message.err("issues")

    elif os.path.exists(THUMB_PATH):
        await userge.send_document(chat_id=message.chat.id,
                                   document=THUMB_PATH,
                                   disable_notification=True,
                                   reply_to_message_id=message.message_id)

        await message.delete()

    else:
        await message.err("Custom Thumbnail Not Found!")
