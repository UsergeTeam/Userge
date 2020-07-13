# By @krishna_singhal

import os

from pyrogram.errors.exceptions.bad_request_400 import YouBlockedUser

from userge import userge, Message, Config
from userge.utils import take_screen_shot, runcmd


@userge.on_cmd("meme", about={
    'header': "Write text on any media. (๑¯ω¯๑)",
    'description': "Top and bottom text are separated by ; ",
    'usage': "{tr}meme [text on top] ; [text on bottom] as a reply."})
async def meme_(message: Message):
    """ meme for media """
    meme_file = None
    replied = message.reply_to_message
    if not (replied and message.input_str):
        await message.err("```Nibba, Reply to Media and Give some input...```", del_in=5)
        return
    if not (replied.photo or replied.sticker or replied.video or replied.animation):
        await message.err("```Reply to only media...```", del_in=5)
        return
    if not os.path.isdir(Config.DOWN_PATH):
        os.makedirs(Config.DOWN_PATH)
    await message.edit("```Memifying...```")
    dls = await message.client.download_media(
        message=replied,
        file_name=Config.DOWN_PATH)
    dls_loc = os.path.join(Config.DOWN_PATH, os.path.basename(dls))
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
        await message.edit("```Memifying this gay sticker...```")
        file_1 = os.path.join(Config.DOWN_PATH, "meme.png")
        cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_loc} {file_1}"
        stdout, stderr = (await runcmd(cmd))[:2]
        if not os.path.lexists(file_1):
            await message.err("```Sticker not found, cuz its gay...```", del_in=5)
            raise Exception(stdout + stderr)
        meme_file = file_1
    elif replied.animation or replied.video:
        if replied.video:
            await message.edit("```Memifying this gay video...```")
        else:
            await message.edit("```What a Gif, Memifying...```")
        file_2 = os.path.join(Config.DOWN_PATH, "meme.png")
        await take_screen_shot(dls_loc, 0, file_2)
        if not os.path.lexists(file_2):
            await message.err("```Media not found...```", del_in=5)
            return
        meme_file = file_2
    elif replied.sticker and replied.sticker.file_name.endswith(".webp"):
        await message.edit("```Memifying this gay sticker...```")
        file_3 = os.path.join(Config.DOWN_PATH, "meme.png")
        os.rename(dls_loc, file_3)
        if not os.path.lexists(file_3):
            await message.err("```Sticker not found...```", del_in=5)
            return
        meme_file = file_3
    if meme_file is None:
        meme_file = dls_loc
    chat = "@MemeAutobot"
    async with userge.conversation(chat) as conv:
        try:
            args = message.input_str
            await conv.send_message("/start")
            await conv.get_response(mark_read=True)
        except YouBlockedUser:
            await message.err(
                "```This cmd not for you, If you want to use, Unblock``` **@MemeAutobot**",
                del_in=5)
            return
        await conv.send_message(args)
        response = await conv.get_response(mark_read=True)
        if "Okay..." in response.text:
            await message.edit("```Sending gay media to gay...```")
        await userge.send_photo(chat, meme_file)
        response = await conv.get_response(mark_read=True)
        if not response.photo:
            await message.err("Bot is Down, try to restart Bot !...", del_in=5)
            return
        message_id = replied.message_id
        Meme_file = None
        if response.photo:
            directory = Config.DOWN_PATH
            file_name = "meme.webp"
            Meme_file = os.path.join(directory, file_name)
            await userge.download_media(
                message=response,
                file_name=Meme_file)
            await userge.send_sticker(
                message.chat.id,
                sticker=Meme_file,
                reply_to_message_id=message_id,
            )
    await message.delete()
    for files in (dls_loc, meme_file, Meme_file):
        if files and os.path.exists(files):
            os.remove(files)
