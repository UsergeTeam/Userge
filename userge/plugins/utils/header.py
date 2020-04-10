import requests
from userge import userge, Message, Config


@userge.on_cmd("head", about="""\
__View headers in URL__

**Available Flags:**

    `-r` : __allow redirects__
    `-s` : __allow streams__
    `-t` : __request timeout__

**Usage:**

    `.head [flags] [url]`
    
**Example:**

    `.head -r -s -t5 https://www.google.com`""")
async def req_head(message: Message):
    await message.edit("Processing ...")

    link = message.filtered_input_str
    flags = message.flags

    red = True if '-r' in flags else False
    stm = True if '-s' in flags else False
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

    if len(output) >= Config.MAX_MESSAGE_LENGTH:
        await message.send_as_file(text=output, caption=link)

    else:
        await message.edit(output, disable_web_page_preview=True)
