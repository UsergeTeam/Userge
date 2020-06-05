# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import requests

from userge import userge, Message


@userge.on_cmd("head", about={
    'header': "View headers in URL",
    'flags': {
        '-r': "allow redirects",
        '-s': "allow streams",
        '-t': "request timeout"},
    'usage': "{tr}head [flags] [url]",
    'examples': "{tr}head -r -s -t5 https://www.google.com"})
async def req_head(message: Message):
    await message.edit("Processing ...")
    link = message.filtered_input_str
    flags = message.flags
    red = '-r' in flags
    stm = '-s' in flags
    tout = int(flags.get('-t', 3))
    if not link:
        await message.err(text="Please give me a link link!")
        return
    try:
        cd = requests.head(url=link,
                           stream=stm,
                           allow_redirects=red,
                           timeout=tout)
    except Exception as i_e:
        await message.err(i_e)
        return
    output = f"**URL**: `{link}`\n\n**STATUS CODE**: __{cd.status_code}__\n\n**HEADERS**:\n\n"
    for k, v in cd.headers.items():
        output += f"   🏷 __{k.lower()}__ : `{v}`\n\n"
    await message.edit_or_send_as_file(text=output, caption=link,
                                       disable_web_page_preview=True)
