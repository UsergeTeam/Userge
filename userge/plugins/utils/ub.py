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


@userge.on_cmd("ub", about="""\
__Searches Urban Dictionary for the query__

**Usage:**

    `.ub [query]`
    
**Exaple:**

    `.ub userge`""")
async def urban_dict(message: Message):
    await message.edit("Processing...")
    query = message.input_str

    if not query:
        await message.err(text="No found any query!")
        return

    try:
        mean = urbandict.define(query)

    except HTTPError:
        await message.err(text=f"Sorry, couldn't find any results for: `{query}``")
        return

    output = ''
    for i, mean_ in enumerate(mean, start=1):
        output += f"**DEF {i}** : __{mean_['def']}__\n" + \
            f"**EX {i}** : __{mean_['example'] or 'not found'}__\n\n"

    if not output:
        await message.err(text=f"No result found for **{query}**")
        return

    output = f"**Query:** `{query}`\n\n{output}"

    await message.edit_or_send_as_file(text=output, caption=query)
