""" Glitch Media """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

# By @Krishna_Singhal

import os

from PIL import Image
from glitch_this import ImageGlitcher

from userge import userge, Message, config
from userge.utils import take_screen_shot, runcmd

Glitched = config.Dynamic.DOWN_PATH + "glitch.gif"


@userge.on_cmd("glitch", about={
    'header': "Reply to any media to glitch",
    'flags': {
        '-s': "Upload glitched IMG as a Sticker"},
    'usage': "{tr}glitch [glitch count] [reply to any media]\n"
             "glitch count = 0 to 8(default is 2)"})
async def glitch_(message: Message):
    """ Create Glitch effect in any media """
    replied = message.reply_to_message
    if not (replied and (
            replied.photo or replied.sticker or replied.video or replied.animation)):
        await message.edit("```Media not found...```")
        await message.reply_sticker('CAADBQADVAUAAjZgsCGE7PH3Wt1wSRYE')
        return
    if message.filtered_input_str:
        if not message.filtered_input_str.isdigit():
            await message.err("```You input is invalid, check help...```", del_in=5)
            return
        input_ = int(message.filtered_input_str)
        if not 0 < input_ < 9:
            await message.err("```Invalid Range...```", del_in=5)
            return
        args = input_
    else:
        args = 2
    if not os.path.isdir(config.Dynamic.DOWN_PATH):
        os.makedirs(config.Dynamic.DOWN_PATH)
    await message.edit("```Glitching... 😁```")
    dls = await message.client.download_media(
        message=replied,
        file_name=config.Dynamic.DOWN_PATH
    )
    dls_loc = os.path.join(config.Dynamic.DOWN_PATH, os.path.basename(dls))
    glitch_file = None
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
        file_1 = os.path.join(config.Dynamic.DOWN_PATH, "glitch.png")
        cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_loc} {file_1}"
        stdout, stderr = (await runcmd(cmd))[:2]
        if not os.path.lexists(file_1):
            await message.err("```Sticker not found...```")
            raise Exception(stdout + stderr)
        glitch_file = file_1
    elif replied.sticker and replied.sticker.file_name.endswith(".webp"):
        file_2 = os.path.join(config.Dynamic.DOWN_PATH, "glitch.png")
        os.rename(dls_loc, file_2)
        if not os.path.lexists(file_2):
            await message.err("```Sticker not found...```")
            return
        glitch_file = file_2
    elif replied.animation or replied.video:
        file_3 = os.path.join(config.Dynamic.DOWN_PATH, "glitch.png")
        await take_screen_shot(dls_loc, 0, file_3)
        if not os.path.lexists(file_3):
            await message.err("```Sticker not found...```")
            return
        glitch_file = file_3
    if glitch_file is None:
        glitch_file = dls_loc
    glitcher = ImageGlitcher()
    img = Image.open(glitch_file)
    message_id = replied.message_id
    if '-s' in message.flags:
        glitched = config.Dynamic.DOWN_PATH + "glitched.webp"
        glitch_img = glitcher.glitch_image(img, args, color_offset=True)
        glitch_img.save(glitched)
        await message.client.send_sticker(
            message.chat.id,
            glitched,
            reply_to_message_id=message_id)
        os.remove(glitched)
        await message.delete()
    else:
        glitch_img = glitcher.glitch_image(img, args, color_offset=True, gif=True)
        DURATION = 200
        LOOP = 0
        glitch_img[0].save(
            Glitched,
            format='GIF',
            append_images=glitch_img[1:],
            save_all=True,
            duration=DURATION,
            loop=LOOP)
        await message.client.send_animation(
            message.chat.id,
            Glitched,
            reply_to_message_id=message_id)
        os.remove(Glitched)
        await message.delete()
    for files in (dls_loc, glitch_file):
        if files and os.path.exists(files):
            os.remove(files)
