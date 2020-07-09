""" Deepfry """

# by @krishna_singhal

import os
from userge.utils import take_screen_shot, runcmd

from pyrogram.errors.exceptions.bad_request_400 import YouBlockedUser

from userge import userge, Config, Message


@userge.on_cmd("fry", about={
    'header': " Deepfrying media",
    'usage': "{tr}fry [lvl from 1 to 8] [reply to sticker and photo]",
    'examples': "{tr}fry 3 [reply to sticker and photo]"})
async def fry_(message: Message):
    """ Deepfry any stickers and images """
    frying_file = None
    replied = message.reply_to_message
    if not (replied and message.input_str):
    	await message.err("```Reply to Media and gib fry count to deepfry !...```", del_in=5)
    	return
    if not (replied.photo or replied.sticker or replied.animation):
    	await message.err("```Reply to Media only !...```", del_in=5)
    	return
    try:
    	args = int(message.input_str)
    except ValueError:
    	args = 1
    if not os.path.isdir(Config.DOWN_PATH):
        os.makedirs(Config.DOWN_PATH)
    await message.edit("```Frying, Wait plox ...```")
    dls = await message.client.download_media( message=replied, file_name=Config.DOWN_PATH)
    dls_loc = os.path.join(Config.DOWN_PATH, os.path.basename(dls))
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
    	webp_file = os.path.join(Config.DOWN_PATH, "fry.png")
    	cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_loc} {webp_file}"
    	stdout, stderr = (await runcmd(cmd))[:2]
    	frying_file = webp_file
    elif replied.animation:
    	jpg_file = os.path.join(Config.DOWN_PATH, "fry.jpg")
    	await take_screen_shot(dls_loc, 0, jpg_file)
    	frying_file = jpg_file
    elif replied.sticker and replied.sticker.file_name.endswith(".webp"):
    	png_file = os.path.join(Config.DOWN_PATH, "fry.jpg")
    	os.rename(dls_loc, png_file)
    	frying_file = png_file
    if frying_file is None:
    	frying_file = dls_loc
    chat = "@image_deepfrybot"
    async with userge.conversation(chat) as conv:
        try:
        	await conv.send_message("/start")
        except YouBlockedUser:
        	await message.edit("**For your kind information, you blocked @Image_DeepfryBot, Unblock it**", del_in=5)
        	return
        await conv.get_response(mark_read=True)
        media = await userge.send_photo(chat, frying_file)
        await conv.get_response(mark_read=True)
        await userge.send_message(chat, "/deepfry {}".format(args), reply_to_message_id=media.message_id)
        response = await conv.get_response(mark_read=True)
        if not response.photo:
        	await message.err("Bot is Down, try to restart Bot !...", del_in=5)
        	return
        message_id = replied.message_id
        if response.photo:
        	directory = Config.DOWN_PATH
        	files_name = "fry.webp"
        	deep_fry = os.path.join(directory, files_name)
        	await userge.download_media(response, file_name=deep_fry)
        	await message.delete()
        	deepfry = Config.DOWN_PATH + "fry.webp"
        	await userge.send_sticker(message.chat.id, sticker=deepfry)
