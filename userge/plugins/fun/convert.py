# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from userge import userge, Message


@userge.on_cmd("small", about="""\
__Make caps smaller__

**Usage:**
    `.small [text | reply to msg]`""")
async def small_(message: Message):
    text = message.input_str
    if message.reply_to_message:
        text = message.reply_to_message.text

    if not text:
        await message.err("input not found")
        return

    await message.edit(text.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                                                    "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘqʀꜱᴛᴜᴠᴡxʏᴢ")))


@userge.on_cmd("lower", about="""\
__Convert text to lowwer__

**Usage:**
    `.lower [text | reply to msg]`""")
async def lower_(message: Message):
    text = message.input_str
    if message.reply_to_message:
        text = message.reply_to_message.text

    if not text:
        await message.err("input not found")
        return

    await message.edit(text.lower())


@userge.on_cmd("upper", about="""\
__Convert text to upper__

**Usage:**
    `.upper [text | reply to msg]`""")
async def upper_(message: Message):
    text = message.input_str
    if message.reply_to_message:
        text = message.reply_to_message.text

    if not text:
        await message.err("input not found")
        return

    await message.edit(text.upper())
