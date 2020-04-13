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

    meanlen = len(mean[0]["def"]) + len(mean[0]["example"])

    if meanlen == 0:
        await message.err(text=f"No result found for **{query}**")
        return

    meaning = '\n'.join([i['def'] for i in mean])
    example = '\n'.join([i['example'] for i in mean])

    output = f"**Query:** `{query}`\n\n\
**Meaning:**\n__{meaning}__\n\n\
**Example:**\n__{example}__"

    await message.edit_or_send_as_file(text=output, caption=query, log=True)
