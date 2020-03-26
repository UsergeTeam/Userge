from userge import userge, Message


@userge.on_cmd("sd (\\d+) (.+)", about="""\
__make self-destructable messages__

**Usage:**

    `.sd [time in seconds] [text]`""")
async def selfdestruct(message: Message):
    seconds = int(message.matches[0].group(1))
    text = str(message.matches[0].group(2))

    await message.edit(text=text, del_in=seconds)
