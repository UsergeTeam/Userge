from urllib.error import HTTPError
import urbandict
from userge import userge, Message, Config


@userge.on_cmd("ub", about="""\
__Searches Urban Dictionary for the query__

**Usage:**

    `.ub query`
    
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

    output = f"**Query:** `{query}`\n\n\
**Meaning:** __{mean[0]['def']}__\n\n\
**Example:**\n__{mean[0]['example']}__"

    if len(output) >= Config.MAX_MESSAGE_LENGTH:
        await message.send_as_file(text=output, caption=query)

    else:
        await message.edit(output)
