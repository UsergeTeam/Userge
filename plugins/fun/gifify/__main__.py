""" Plugin for tgs to GiF """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

# By @Krishna_Singhal

import os

import lottie

from userge import userge, Message, config, pool


@userge.on_cmd("gif", about={
    'header': "Convert Telegram Animated Sticker to GiF",
    'usage': "{tr}gif [quality (optional)] [reply to sticker]\n"
             "Max quality : 720p",
    'examples': [
        "{tr}gif [reply to sticker]",
        "{tr}gif 512 [reply to Sticker]"]})
async def gifify(msg: Message):
    """ Convert Animated Sticker to GiF """
    replied = msg.reply_to_message
    if not (replied and replied.sticker and replied.sticker.file_name.endswith(".tgs")):
        await msg.err("Reply to Animated Sticker Only to Convert GiF", del_in=5)
        return
    if msg.input_str:
        if not msg.input_str.isdigit():
            await msg.err("Invalid given quality, Check help", del_in=5)
            return
        input_ = int(msg.input_str)
        if not 0 < input_ < 721:
            await msg.err("Invalid quality range, Check help", del_in=5)
            return
        quality = input_
    else:
        quality = 512
    if not os.path.isdir(config.Dynamic.DOWN_PATH):
        os.makedirs(config.Dynamic.DOWN_PATH)
    await msg.try_to_edit("```Converting this Sticker to GiF...\n"
                          "This may takes upto few mins...```")
    dls = await msg.client.download_media(replied, file_name=config.Dynamic.DOWN_PATH)
    converted_gif = await _tgs_to_gif(dls, quality)
    await msg.client.send_animation(
        msg.chat.id,
        converted_gif,
        unsave=True,
        reply_to_message_id=replied.message_id)
    await msg.delete()
    os.remove(converted_gif)


@pool.run_in_thread
def _tgs_to_gif(sticker_path: str, quality: int = 256) -> str:
    dest = os.path.join(config.Dynamic.DOWN_PATH, "animation.gif")
    with open(dest, 'wb') as t_g:
        lottie.exporters.gif.export_gif(lottie.parsers.tgs.parse_tgs(sticker_path), t_g, quality, 1)
    os.remove(sticker_path)
    return dest
