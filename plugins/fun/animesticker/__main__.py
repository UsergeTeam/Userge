""" Creates random anime sticker """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

# By @Krishna_Singhal

import random

from emoji import get_emoji_regexp

from userge import userge, Message


@userge.on_cmd("sticker", about={
    'header': "Creates random anime sticker",
    'flags': {
        '-f': "To get only girls in anime",
        '-ggl': "To get google search sticker",
        '-mock': "get mock text in sticker"},
    'usage': "{tr}sticker [text | reply to message]\n"
             "{tr}sticker [flags] [text | reply to message]",
    'examples': [
        "{tr}sticker Hello boys and girls",
        "{tr}sticker [flags] Hello boys and girls"]}, allow_via_bot=False)
async def anime_sticker(message: Message):
    """ Creates random anime sticker! """
    replied = message.reply_to_message
    args = message.filtered_input_str
    if args:
        text = args
    elif replied:
        text = args if args else replied.text
    else:
        await message.err("Input not found!")
        return
    await message.delete()
    if '-ggl' in message.flags:
        try:
            stickers = await userge.get_inline_bot_results(
                "stickerizerbot",
                f"#12{get_emoji_regexp().sub(u'', text)}")
            await userge.send_inline_bot_result(
                chat_id=message.chat.id,
                query_id=stickers.query_id,
                result_id=stickers.results[0].id)
        except IndexError:
            await message.err("List index out of range")
        else:
            await message.delete()
            return
    if '-f' in message.flags:
        k = [20, 32, 33, 40, 41, 42, 58]
        animus = random.choice(k)
    elif '-mock' in message.flags:
        animus = 7
    else:
        k = [1, 3, 7, 9, 13, 22, 34, 35, 36, 37, 43, 44, 45, 52, 53, 55]
        animus = random.choice(k)
    try:
        stickers = await userge.get_inline_bot_results(
            "stickerizerbot",
            f"#{animus}{get_emoji_regexp().sub(u'', text)}"
        )
        saved = await userge.send_inline_bot_result(
            chat_id="me",
            query_id=stickers.query_id,
            result_id=stickers.results[0].id
        )
        saved = await userge.get_messages("me", int(saved.updates[1].message.id))
        message_id = replied.message_id if replied else None
        await userge.send_sticker(
            chat_id=message.chat.id,
            sticker=str(saved.sticker.file_id),
            reply_to_message_id=message_id
        )
        await saved.delete()
    except IndexError:
        await message.err("List index out of range")
