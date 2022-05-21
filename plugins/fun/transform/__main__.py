""" Ghost, filp/mirror, rotate """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

# By @Krishna_Singhal

import os

from PIL import Image, ImageOps

from userge import userge, Message, config
from userge.utils import take_screen_shot, runcmd

Converted = config.Dynamic.DOWN_PATH + "sticker.webp"


@userge.on_cmd("(ghost|invert)", about={
    'header': "Invert media as looking like a ghost",
    'usage': "{tr}ghost [reply to any media]\n"
             "{tr}invert [reply to any media]"}, name="ghost")
async def ghost_invert(message: Message):
    """ Transform IMG as looking like a ghost """
    replied = message.reply_to_message
    if not (replied and (
            replied.photo or replied.sticker or replied.video or replied.animation)):
        await message.edit("```Media not found...```")
        await message.reply_sticker('CAADBQADVAUAAjZgsCGE7PH3Wt1wSRYE')
        return
    if not os.path.isdir(config.Dynamic.DOWN_PATH):
        os.makedirs(config.Dynamic.DOWN_PATH)
    await message.edit("```Wait, Ghost is coming 😈```")
    dls = await message.client.download_media(
        message=replied,
        file_name=config.Dynamic.DOWN_PATH
    )
    dls_loc = os.path.join(config.Dynamic.DOWN_PATH, os.path.basename(dls))
    ghost_file = None
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
        await message.edit("```Ghost is coming from Animated Sticker```")
        file_1 = os.path.join(config.Dynamic.DOWN_PATH, "ghost.png")
        cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_loc} {file_1}"
        stdout, stderr = (await runcmd(cmd))[:2]
        if not os.path.lexists(file_1):
            await message.err("```Ghost ran away```")
            raise Exception(stdout + stderr)
        ghost_file = file_1
    elif replied.sticker and replied.sticker.file_name.endswith(".webp"):
        await message.edit("```Ghost coming from this gay sticker```")
        file_2 = os.path.join(config.Dynamic.DOWN_PATH, "ghost.png")
        os.rename(dls_loc, file_2)
        if not os.path.lexists(file_2):
            await message.err("```Ghost ran away```")
            return
        ghost_file = file_2
    elif replied.animation or replied.video:
        if replied.animation:
            await message.edit("```Ghost coming from this gay GIF```")
        else:
            await message.edit("```Ghost coming from this gay video```")
        file_3 = os.path.join(config.Dynamic.DOWN_PATH, "ghost.jpg")
        await take_screen_shot(dls_loc, 0, file_3)
        if not os.path.lexists(file_3):
            await message.err("```Ghost ran away```")
            return
        ghost_file = file_3
    if ghost_file is None:
        ghost_file = dls_loc
    im = Image.open(ghost_file).convert('RGB')
    im_invert = ImageOps.invert(im)
    im_invert.save(Converted)
    await message.client.send_sticker(
        message.chat.id,
        sticker=Converted,
        reply_to_message_id=replied.message_id)
    await message.delete()
    for files in (dls_loc, ghost_file, Converted):
        if files and os.path.exists(files):
            os.remove(files)


@userge.on_cmd("(mirror|flip)", about={
    'header': "Mirror and flip any media",
    'usage': "{tr}mirror [reply to any media]\n"
             "{tr}flip [reply to any media]"}, name="mirror")
async def mirror_flip(message: Message):
    """ Mirror or flip IMG """
    replied = message.reply_to_message
    if not (replied and (
            replied.photo or replied.sticker or replied.video or replied.animation)):
        await message.edit("```Media not found...```")
        await message.reply_sticker('CAADBQADVAUAAjZgsCGE7PH3Wt1wSRYE')
        return
    if not os.path.isdir(config.Dynamic.DOWN_PATH):
        os.makedirs(config.Dynamic.DOWN_PATH)
    Cmd = message.matches[0].group(1).lower()
    await message.edit("```Wait, let me converting your media 😉```")
    dls = await message.client.download_media(
        message=replied,
        file_name=config.Dynamic.DOWN_PATH
    )
    dls_loc = os.path.join(config.Dynamic.DOWN_PATH, os.path.basename(dls))
    mirror_flip_file = None
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
        file_1 = os.path.join(config.Dynamic.DOWN_PATH, "img.png")
        cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_loc} {file_1}"
        stdout, stderr = (await runcmd(cmd))[:2]
        if not os.path.lexists(file_1):
            await message.err("```Sticker not found```")
            raise Exception(stdout + stderr)
        mirror_flip_file = file_1
    elif replied.sticker and replied.sticker.file_name.endswith(".webp"):
        file_2 = os.path.join(config.Dynamic.DOWN_PATH, "img.png")
        os.rename(dls_loc, file_2)
        if not os.path.lexists(file_2):
            await message.err("```Sticker not found```")
            return
        mirror_flip_file = file_2
    elif replied.animation or replied.video:
        file_3 = os.path.join(config.Dynamic.DOWN_PATH, "img.jpg")
        await take_screen_shot(dls_loc, 0, file_3)
        if not os.path.lexists(file_3):
            await message.err("```Sticker not found```")
            return
        mirror_flip_file = file_3
    if mirror_flip_file is None:
        mirror_flip_file = dls_loc
    im = Image.open(mirror_flip_file).convert('RGB')
    if Cmd == "mirror":
        IMG = ImageOps.mirror(im)
    else:
        IMG = ImageOps.flip(im)
    IMG.save(Converted, quality=95)
    await message.client.send_sticker(
        message.chat.id,
        sticker=Converted,
        reply_to_message_id=replied.message_id)
    await message.delete()
    for files in (dls_loc, mirror_flip_file, Converted):
        if files and os.path.exists(files):
            os.remove(files)


@userge.on_cmd("rotate", about={
    'header': "Rotate any media",
    'usage': "{tr}rotate [angle to rotate] [reply to media]\n"
             "angle = 0 to 360(default is 90)"})
async def rotate_(message: Message):
    """ Rotate IMG to any angle """
    replied = message.reply_to_message
    if not (replied and (
            replied.photo or replied.sticker or replied.video or replied.animation)):
        await message.edit("```Media not found...```")
        await message.reply_sticker('CAADBQADVAUAAjZgsCGE7PH3Wt1wSRYE')
        return
    if message.input_str:
        if not message.input_str.isdigit():
            await message.err("```You input is invalid, check help...```", del_in=5)
            return
        input_ = int(message.input_str)
        if not 0 < input_ < 360:
            await message.err("```Invalid Angle...```", del_in=5)
            return
        args = input_
    else:
        args = 90
    if not os.path.isdir(config.Dynamic.DOWN_PATH):
        os.makedirs(config.Dynamic.DOWN_PATH)
    await message.edit("```Wait, let me Rotating Your media ☺️```")
    dls = await message.client.download_media(
        message=replied,
        file_name=config.Dynamic.DOWN_PATH
    )
    dls_loc = os.path.join(config.Dynamic.DOWN_PATH, os.path.basename(dls))
    rotate_file = None
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
        file_1 = os.path.join(config.Dynamic.DOWN_PATH, "img.png")
        cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_loc} {file_1}"
        stdout, stderr = (await runcmd(cmd))[:2]
        if not os.path.lexists(file_1):
            await message.err("```Sticker not found```")
            raise Exception(stdout + stderr)
        rotate_file = file_1
    elif replied.sticker and replied.sticker.file_name.endswith(".webp"):
        file_2 = os.path.join(config.Dynamic.DOWN_PATH, "img.png")
        os.rename(dls_loc, file_2)
        if not os.path.lexists(file_2):
            await message.err("```Sticker not found```")
            return
        rotate_file = file_2
    elif replied.animation or replied.video:
        file_3 = os.path.join(config.Dynamic.DOWN_PATH, "img.jpg")
        await take_screen_shot(dls_loc, 0, file_3)
        if not os.path.lexists(file_3):
            await message.err("```Sticker not found```")
            return
        rotate_file = file_3
    if rotate_file is None:
        rotate_file = dls_loc
    im = Image.open(rotate_file).convert('RGB')
    IMG = im.rotate(args, expand=1)
    IMG.save(Converted, quality=95)
    await message.client.send_sticker(
        message.chat.id,
        sticker=Converted,
        reply_to_message_id=replied.message_id)
    await message.delete()
    for files in (dls_loc, rotate_file, Converted):
        if files and os.path.exists(files):
            os.remove(files)
