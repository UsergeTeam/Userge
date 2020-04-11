# Copyright (C) 2020 by UsergeTeam@Telegram, < https://t.me/theUserge >.
#
# This file is part of < https://github.com/uaudith/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import os
import time
from datetime import datetime
from PIL import Image
from userge import userge, Config, Message
from userge.utils import progress

THUMB_PATH = Config.DOWN_PATH + "thumb_image.jpg"


@userge.on_cmd('sthumb', about="""\
__Save thumbnail__

**Usage:**

    `.sthumb [reply to any photo]`""")
async def save_thumb_nail(message: Message):
    await message.edit("processing ...")
    if message.reply_to_message is not None and message.reply_to_message.photo:
        start_t = datetime.now()
        c_time = time.time()

        d_f_name = await userge.download_media(message=message.reply_to_message,
                                               file_name=Config.DOWN_PATH,
                                               progress=progress,
                                               progress_args=(
                                                   "trying to download", message, c_time))

        Image.open(d_f_name).convert("RGB").save(THUMB_PATH, 'JPEG')
        os.remove(d_f_name)
        end_t = datetime.now()
        ms = (end_t - start_t).seconds

        await message.edit(f"thumbnail saved in {ms} seconds.", del_in=3)

    else:
        await message.edit("Reply to a photo to save custom thumbnail", del_in=3)


@userge.on_cmd('dthumb', about="__Delete thumbnail__")
async def clear_thumb_nail(message: Message):
    await message.edit("`processing ...`")
    if os.path.exists(THUMB_PATH):
        os.remove(THUMB_PATH)

    await message.edit("✅ Custom thumbnail deleted succesfully.", del_in=3)


@userge.on_cmd('vthumb', about="__View thumbnail__")
async def get_thumb_nail(message: Message):
    await message.edit("processing ...")
    if os.path.exists(THUMB_PATH):
        await userge.send_document(chat_id=message.chat.id,
                                   document=THUMB_PATH,
                                   disable_notification=True,
                                   reply_to_message_id=message.message_id)

        await message.delete()

    else:
        await message.err("Custom Thumbnail Not Found!")
