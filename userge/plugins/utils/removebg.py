# Userge Plugin for removing background from Images
# Author: Sumanjay (https://github.com/cyberboysumanjay) (@cyberboysumanjay)
# All rights reserved.

import os
import time
from datetime import datetime

from removebg import RemoveBg

from userge import userge, Config, Message
from userge.utils import progress

IMG_PATH = Config.DOWN_PATH + "dl_image.jpg"


@userge.on_cmd('removebg', about={
    'header': "Removes Background from Image (50 Calls per Month in the free API)",
    'usage': "{tr}removebg [reply to any photo | direct link of photo]"})
async def remove_background(message: Message):
    if not Config.REMOVE_BG_API_KEY:
        await message.edit(
            "Get the API from <a href='https://www.remove.bg/b/background-removal-api'>HERE "
            "</a> & add it to Heroku Config Vars <code>REMOVE_BG_API_KEY</code>",
            disable_web_page_preview=True, parse_mode="html")
        return
    await message.edit("Analysing...")
    replied = message.reply_to_message
    if (replied and replied.media
            and (replied.photo
                 or (replied.document and "image" in replied.document.mime_type))):
        start_t = datetime.now()
        c_time = time.time()
        if os.path.exists(IMG_PATH):
            os.remove(IMG_PATH)
        await message.client.download_media(message=replied,
                                            file_name=IMG_PATH,
                                            progress=progress,
                                            progress_args=(
                                                "Downloading Image", userge, message, c_time))
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(f"Image saved in {m_s} seconds.\nRemoving Background Now...")
        # Cooking Image
        try:
            rmbg = RemoveBg(Config.REMOVE_BG_API_KEY, "removebg_error.log")
            rmbg.remove_background_from_img_file(IMG_PATH)
            RBG_IMG_PATH = IMG_PATH + "_no_bg.png"
            start_t = datetime.now()
            c_time = time.time()
            await message.client.send_document(
                chat_id=message.chat.id,
                document=RBG_IMG_PATH,
                disable_notification=True,
                progress=progress,
                progress_args=(
                    "Uploading", userge, message, c_time, str(RBG_IMG_PATH)
                )
            )
            await message.delete()
        except Exception:
            await message.edit("Something went wrong!\nCheck your usage quota!")
            return
    else:
        await message.edit("Reply to a photo to remove background!", del_in=5)
