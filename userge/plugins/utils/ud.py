# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from urllib.error import HTTPError

import urbandict

from userge import userge, Message


@userge.on_cmd("ud", about={
    'header': "Searches Urban Dictionary for the query",
    'flags': {'-l': "limit : defaults to 1"},
    'usage': "{tr}ud [flag] [query]",
    'examples': ["{tr}ud userge", "{tr}ud -l3 userge"]})
async def urban_dict(message: Message):
    await message.edit("Processing...")
    query = message.filtered_input_str
    if not query:
        await message.err(text="No found any query!")
        return
    try:
        mean = urbandict.define(query)
    except HTTPError:
        await message.err(text=f"Sorry, couldn't find any results for: `{query}``")
        return
    output = ''
    limit = int(message.flags.get('-l', 1))
    for i, mean_ in enumerate(mean, start=1):
        output += f"{i}. **{mean_['def']}**\n" + \
            f"  Examples:\n  * `{mean_['example'] or 'not found'}`\n\n"
        if limit <= i:
            break
    if not output:
        await message.err(text=f"No result found for **{query}**")
        return
    output = f"**Query:** `{query}`\n**Limit:** `{limit}`\n\n{output}"
    await message.edit_or_send_as_file(text=output, caption=query)
