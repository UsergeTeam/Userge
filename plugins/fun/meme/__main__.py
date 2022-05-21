""" write text on images """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

# By @krishna_singhal

import os

from pyrogram.errors.exceptions.bad_request_400 import YouBlockedUser

from userge import userge, Message, config
from userge.utils import take_screen_shot, runcmd


@userge.on_cmd("meme", about={
    'header': "Write text on any media. (๑¯ω¯๑)",
    'description': "Top and bottom text are separated by ; ",
    'usage': "{tr}meme [text on top] ; [text on bottom] as a reply."}, allow_via_bot=False)
async def meme_(message: Message):
    """ meme for media """
    replied = message.reply_to_message
    if not (replied and message.input_str):
        await message.err("Nibba, reply to Media and give some input...")
        return
    if not (replied.photo or replied.sticker or replied.video or replied.animation):
        await message.err("reply to only media...")
        return
    if not os.path.isdir(config.Dynamic.DOWN_PATH):
        os.makedirs(config.Dynamic.DOWN_PATH)
    await message.edit("`Memifying...`")

    meme_file = None
    should_forward = False
    dls_loc = None

    if (replied.photo or (
        replied.sticker and replied.sticker.file_name.endswith(".webp")
    )):
        should_forward = True
    else:
        dls = await message.client.download_media(
            message=replied,
            file_name=config.Dynamic.DOWN_PATH)
        dls_loc = os.path.join(config.Dynamic.DOWN_PATH, os.path.basename(dls))
        if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
            file_1 = os.path.join(config.Dynamic.DOWN_PATH, "meme.png")
            cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_loc} {file_1}"
            stdout, stderr = (await runcmd(cmd))[:2]
            if not os.path.lexists(file_1):
                await message.err("Sticker not found, cuz its gay...")
                raise Exception(stdout + stderr)
            meme_file = file_1
        elif replied.animation or replied.video:
            file_2 = os.path.join(config.Dynamic.DOWN_PATH, "meme.png")
            await take_screen_shot(dls_loc, 0, file_2)
            if not os.path.lexists(file_2):
                await message.err("Media not found...")
                return
            meme_file = file_2

    chat = "@MemeAuto_bot"
    async with userge.conversation(chat) as conv:
        try:
            await conv.send_message("/start")
            await conv.get_response(mark_read=True)
        except YouBlockedUser:
            await message.err(
                "this cmd not for you, If you want to use, Unblock **@MemeAutobot**",
                del_in=5)
            return
        if should_forward:
            await conv.forward_message(replied)
        else:
            await userge.send_photo(chat, meme_file)
        response = await conv.get_response(mark_read=True)
        if "Okay..." not in response.text:
            await message.err("Bot is Down, try to restart Bot !...")
            return
        await conv.send_message(message.input_str)
        response = await conv.get_response(mark_read=True)
        if response.sticker:
            await response.copy(message.chat.id, reply_to_message_id=replied.message_id)
    await message.delete()
    for file in (meme_file, dls_loc):
        if file and os.path.exists(file):
            os.remove(file)
