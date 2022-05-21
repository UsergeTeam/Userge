""" deepfry and fry for frying any media """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import random

from PIL import Image, ImageEnhance, ImageOps
from pyrogram.errors.exceptions.bad_request_400 import YouBlockedUser

from userge import userge, Message, config
from userge.utils import progress, take_screen_shot, runcmd


@userge.on_cmd("deepfry", about={
    'header': "Deep Fryer",
    'description': "Well deepfy any image/sticker/gif and make it look ugly",
    'usage': "{tr}deepfry [fry count] as a reply.",
    'examples': "{tr}deepfry 1"})
async def deepfryer(message: Message):
    """ deepfryer """
    replied = message.reply_to_message
    if not (replied and message.input_str):
        await message.edit("LMAO no one's gonna help you, if u use .help now then u **Gey**")
        await message.reply_sticker(sticker="CAADAQADhAAD3gkwRviGxMVn5813FgQ")
        return
    if not (replied.photo or replied.sticker or replied.video or replied.animation):
        await message.edit("Bruh, U Comedy me? Can you deepfry rocks?")
        return
    try:
        fry_c = int(message.input_str)
    except ValueError:
        fry_c = 1
    if not os.path.isdir(config.Dynamic.DOWN_PATH):
        os.makedirs(config.Dynamic.DOWN_PATH)
    await message.edit("*turns on fryer*")
    dls = await message.client.download_media(
        message=message.reply_to_message,
        file_name=config.Dynamic.DOWN_PATH,
        progress=progress,
        progress_args=(message, "Lemme add some seasonings")
    )
    dls_loc = os.path.join(config.Dynamic.DOWN_PATH, os.path.basename(dls))
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
        await message.edit("wait fryer is cold naw")
        png_file = os.path.join(config.Dynamic.DOWN_PATH, "meme.png")
        cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_loc} {png_file}"
        stdout, stderr = (await runcmd(cmd))[:2]
        os.remove(dls_loc)
        if not os.path.lexists(png_file):
            await message.err("*boom* fryer exploded, can't deepfry this")
            raise Exception(stdout + stderr)
        dls_loc = png_file
    elif replied.animation or replied.video:
        await message.edit("wait putting some more oil in fryer")
        jpg_file = os.path.join(config.Dynamic.DOWN_PATH, "meme.jpg")
        await take_screen_shot(dls_loc, 0, jpg_file)
        os.remove(dls_loc)
        if not os.path.lexists(jpg_file):
            await message.err("someone took my oil can't deepfry it.")
            return
        dls_loc = jpg_file

    await message.edit("time to put this in fryer 🔥")
    fried_file = await deepfry(dls_loc)
    if fry_c > 1:
        for _ in range(fry_c):
            fried_file = await deepfry(fried_file)

    await message.client.send_photo(chat_id=message.chat.id,
                                    photo=fried_file,
                                    reply_to_message_id=replied.message_id)
    await message.delete()
    os.remove(fried_file)


async def deepfry(img):

    img = Image.open(img)
    colours = ((random.randint(50, 200), random.randint(40, 170),
                random.randint(40, 190)), (random.randint(190, 255),
                                           random.randint(170, 240),
                                           random.randint(180, 250)))

    img = img.convert("RGB")
    width, height = img.width, img.height
    img = img.resize((int(width**random.uniform(
        0.8, 0.9)), int(height**random.uniform(0.8, 0.9))), resample=Image.LANCZOS)
    img = img.resize((int(width**random.uniform(
        0.85, 0.95)), int(height**random.uniform(0.85, 0.95))), resample=Image.BILINEAR)
    img = img.resize((int(width**random.uniform(
        0.89, 0.98)), int(height**random.uniform(0.89, 0.98))), resample=Image.BICUBIC)
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, random.randint(3, 7))

    overlay = img.split()[0]
    overlay = ImageEnhance.Contrast(overlay).enhance(random.uniform(1.0, 2.0))
    overlay = ImageEnhance.Brightness(overlay).enhance(random.uniform(
        1.0, 2.0))

    overlay = ImageOps.colorize(overlay, colours[0], colours[1])

    img = Image.blend(img, overlay, random.uniform(0.1, 0.4))
    img = ImageEnhance.Sharpness(img).enhance(random.randint(5, 300))

    image_name = "deepfried.jpeg"
    fried_file = os.path.join(config.Dynamic.DOWN_PATH, image_name)
    img.save(fried_file, "JPEG")
    return fried_file


# fry by @krishna_singhal


@userge.on_cmd("fry", about={
    'header': "frying media",
    'usage': "{tr}fry [fry count (recommendation 3)] [reply to any media]",
    'examples': "{tr}fry 3 [reply to any media]"}, allow_via_bot=False)
async def fry_(message: Message):
    """ fryer for any media """
    frying_file = None
    replied = message.reply_to_message
    if not (replied and message.input_str):
        await message.err("Reply to Media and gib fry count to deepfry !...")
        return
    if not (replied.photo or replied.sticker or replied.video or replied.animation):
        await message.err("Reply to Media only !...")
        return
    args = message.input_str
    if not args.isdigit():
        await message.err("Need fry count from 1 - 8 only !...")
        return
    args = int(args)
    if not 0 < args < 9:
        await message.err("Invalid range !...")
        return
    if not os.path.isdir(config.Dynamic.DOWN_PATH):
        os.makedirs(config.Dynamic.DOWN_PATH)
    await message.edit("`Frying, Wait plox ...`")
    dls = await message.client.download_media(
        message=replied,
        file_name=config.Dynamic.DOWN_PATH,
        progress=progress,
        progress_args=(message, "Downloading to my local")
    )
    dls_loc = os.path.join(config.Dynamic.DOWN_PATH, os.path.basename(dls))
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
        await message.edit("```Ohh nice sticker, Lemme deepfry this Animated sticker ...```")
        webp_file = os.path.join(config.Dynamic.DOWN_PATH, "fry.png")
        cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_loc} {webp_file}"
        stdout, stderr = (await runcmd(cmd))[:2]
        if not os.path.lexists(webp_file):
            await message.err("```Media not found ...```", del_in=5)
            raise Exception(stdout + stderr)
        frying_file = webp_file
    elif replied.animation or replied.video:
        if replied.video:
            await message.edit("```Wait bruh, lemme deepfry this video ...```")
        else:
            await message.edit("```What a Gif, Lemme deepfry this ...```")
        jpg_file = os.path.join(config.Dynamic.DOWN_PATH, "fry.jpg")
        await take_screen_shot(dls_loc, 0, jpg_file)
        if not os.path.lexists(jpg_file):
            await message.err("```Media not found ...```", del_in=5)
            return
        frying_file = jpg_file
    elif replied.sticker and replied.sticker.file_name.endswith(".webp"):
        await message.edit("```Lemme deepfry this Sticker, wait plox ...```")
        png_file = os.path.join(config.Dynamic.DOWN_PATH, "fry.jpg")
        os.rename(dls_loc, png_file)
        if not os.path.lexists(png_file):
            await message.err("```Media not found ...```", del_in=5)
            return
        frying_file = png_file
    if frying_file is None:
        frying_file = dls_loc
    chat = "@image_deepfrybot"
    async with userge.conversation(chat) as conv:
        try:
            await conv.send_message("/start")
        except YouBlockedUser:
            await message.edit(
                "**For your kind information, you blocked @Image_DeepfryBot, Unblock it**",
                del_in=5)
            return
        await conv.get_response(mark_read=True)
        media = await userge.send_photo(chat, frying_file)
        await conv.get_response(mark_read=True)
        await userge.send_message(
            chat,
            "/deepfry {}".format(args),
            reply_to_message_id=media.message_id,
        )
        response = await conv.get_response(mark_read=True)
        if not response.photo:
            await message.err("Bot is Down, try to restart Bot !...", del_in=5)
            return
        message_id = replied.message_id
        deep_fry = None
        if response.photo:
            directory = config.Dynamic.DOWN_PATH
            files_name = "fry.webp"
            deep_fry = os.path.join(directory, files_name)
            await message.client.download_media(
                message=response,
                file_name=deep_fry)
            await message.client.send_sticker(
                message.chat.id,
                sticker=deep_fry,
                reply_to_message_id=message_id,
            )
    await message.delete()
    for garb in (dls_loc, frying_file, deep_fry):
        if garb and os.path.exists(garb):
            os.remove(garb)
