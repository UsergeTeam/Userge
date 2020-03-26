from userge import userge, Message


@userge.on_cmd("s", about="__to search commands in **USERGE**__")
async def search(message: Message):
    cmd = message.input_str

    if not cmd:
        await message.err(text="Enter any keyword to search in commands")
        return

    found = '\n.'.join([i for i in sorted(userge.get_help()) \
        if cmd.lstrip('.') in i])

    if found:
        out = f"**--I found these commands:--**\n\n`.{found}`"

    else:
        out = "__command not found!__"

    await message.edit(text=out, del_in=15)
