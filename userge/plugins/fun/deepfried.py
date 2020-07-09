""" Deepfry """

# by @krishna_singhal

import os

from pyrogram.errors.exceptions.bad_request_400 import YouBlockedUser

from userge import userge, Message, Config
from userge.utils import take_screen_shot, runcmd


@userge.on_cmd("fry", about={
    'header': " Deepfrying media",
    'usage': "{tr}fry [fry count (recommendation 3)] [reply to any media]",
    'examples': "{tr}fry 3 [reply to any media]"})
async def fry_(message: Message):
    """ Deepfry any stickers and images """
    frying_file = None
    replied = message.reply_to_message
    if not (replied and message.input_str):
        await message.err("```Reply to Media and gib fry count to deepfry !...```", del_in=5)
        return
    if not (replied.photo or replied.sticker or replied.video or replied.animation):
        await message.err("```Reply to Media only !...```", del_in=5)
        return
    args = message.input_str
    if not args.isdigit():
        await message.err("```Need fry count from 1 - 8 only !...```", del_in=5)
        return
    args = int(args)
    if not (0 < args < 9):
        await message.err("```Invalid range !...```", del_in=5)
        return
    if not os.path.isdir(Config.DOWN_PATH):
        os.makedirs(Config.DOWN_PATH)
    await message.edit("```Frying, Wait plox ...```")
    dls = await message.client.download_media(message=replied, file_name=Config.DOWN_PATH)
    dls_loc = os.path.join(Config.DOWN_PATH, os.path.basename(dls))
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
        await message.edit("```Ohh nice sticker, Lemme deepfry this Animated sticker ...```")
        webp_file = os.path.join(Config.DOWN_PATH, "fry.png")
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
        jpg_file = os.path.join(Config.DOWN_PATH, "fry.jpg")
        await take_screen_shot(dls_loc, 0, jpg_file)
        if not os.path.lexists(jpg_file):
            await message.err("```Media not found ...```", del_in=5)
            return
        frying_file = jpg_file
    elif replied.sticker and replied.sticker.file_name.endswith(".webp"):
        await message.edit("```Lemme deepfry this Sticker, wait plox ...```")
        png_file = os.path.join(Config.DOWN_PATH, "fry.jpg")
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
            directory = Config.DOWN_PATH
            files_name = "fry.webp"
            deep_fry = os.path.join(directory, files_name)
            await userge.download_media(
                message=response,
                file_name=deep_fry)
            await userge.send_sticker(
                message.chat.id,
                sticker=deep_fry,
                reply_to_message_id=message_id,
            )
    await message.delete()
    for garb in (dls_loc, frying_file, deep_fry):
        if garb and os.path.exists(garb):
            os.remove(garb)
