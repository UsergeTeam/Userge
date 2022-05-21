""" give head pat """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

from random import choice
from urllib import parse

import aiohttp

from userge import userge, Message


@userge.on_cmd("pat", about={
    'header': "Give head Pat xD",
    'flags': {'-g': "For Pat Gifs"},
    'usage': "{tr}pat [reply | username]\n{tr}pat -g [reply]"})
async def pat(message: Message):
    username = message.filtered_input_str
    reply = message.reply_to_message
    reply_id = reply.message_id if reply else message.message_id
    if not username and not reply:
        await message.edit("**Bruh** ~`Reply to a message or provide username`", del_in=3)
        return
    kwargs = {"reply_to_message_id": reply_id, "caption": username}

    if "-g" in message.flags:
        async with aiohttp.ClientSession() as session, session.get(
            "https://nekos.life/api/pat"
        ) as request:
            result = await request.json()
            link = result.get("url")
            await message.client.send_animation(
                message.chat.id, animation=link, **kwargs
            )
    else:
        async with aiohttp.ClientSession() as session:
            chi_c = await session.get("https://headp.at/js/pats.json")
            uri = f"https://headp.at/pats/{parse.quote(choice(await chi_c.json()))}"
        await message.reply_photo(uri, **kwargs)

    await message.delete()  # hmm
