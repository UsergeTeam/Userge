# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
from PIL import Image
from telegraph import upload_file
from userge.utils import post_to_telegraph
from userge import userge, Message, Config
from userge.utils import progress

_T_LIMIT = 5242880


@userge.on_cmd("telegraph", about={
    'header': "Upload file to Telegra.ph's servers",
    'types': ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webp'],
    'usage': "reply {tr}telegraph to supported media : limit 5MB"})
async def telegraph_(message: Message):
    replied = message.reply_to_message
    if not replied:
        await message.err("reply to supported media")
        return
    if not ((replied.photo and replied.photo.file_size <= _T_LIMIT)
            or (replied.animation and replied.animation.file_size <= _T_LIMIT)
            or (replied.video and replied.video.file_name.endswith('.mp4')
                and replied.video.file_size <= _T_LIMIT)
            or (replied.sticker)
            or (replied.document
                and replied.document.file_name.endswith(
                    ('.jpg', '.jpeg', '.png', '.gif', '.mp4'))
                and replied.document.file_size <= _T_LIMIT)):
        await message.err("not supported!")
        return
    await message.edit("`processing...`")
    dl_loc = await message.client.download_media(
        message=message.reply_to_message,
        file_name=Config.DOWN_PATH,
        progress=progress,
        progress_args=(message, "trying to download")
    )
    if replied.sticker:
        img = Image.open(dl_loc).convert('RGB')
        img.save(f'{Config.DOWN_PATH}/userge.png', 'png')
        os.remove(dl_loc)
        dl_loc = f'{Config.DOWN_PATH}/userge.png'
    await message.edit("`uploading to telegraph...`")
    try:
        response = upload_file(dl_loc)
    except Exception as t_e:
        await message.err(t_e)
    else:
        await message.edit(f"**[Here Your Telegra.ph Link!](https://telegra.ph{response[0]})**")
    finally:
        os.remove(dl_loc)

@userge.on_cmd("telepaste", about={
    'header': "Paste text to telegraph with custom header(you can use html code.)",
    'usage': "{tr}telepaste [content | reply to msg]",
    'examples': "{tr}telepaste This is header|This is my content"})
async def telepaste(message: Message):
    await message.edit("Please wait.....")
    content = message.input_str
    if message.reply_to_message:
       content = message.reply_to_message.text
    if not content:
        await message.err(text="Please check `.help .telepaste`")
        return
    if "|" in content:
        content = content.split("|")
        if len(content) == 2:
            header = content[0]
            text = content[1]  
        else:
            text = content
            header = "Pasted content by @theuserge"
    else:
        text = content
        header = "Pasted content by @theuserge"
    t_url = post_to_telegraph(header, text)
    await message.edit(text=f"Your text pasted to [telegraph]({t_url})")
