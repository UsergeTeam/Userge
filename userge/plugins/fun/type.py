import time
import random
from pyrogram.errors.exceptions import FloodWait
from userge import userge, Message


@userge.on_cmd("type", about="""\
__Simulate a typewriter__

**Usage:**
    `.type [text | reply to msg]`""")
async def type_(message: Message):
    text = message.input_str
    if message.reply_to_message:
        text = message.reply_to_message.text

    if not text:
        await message.err("input not found")
        return

    s_time = 0.1
    typing_symbol = '|'
    old_text = ''

    await message.edit(typing_symbol)
    time.sleep(s_time)

    for character in text:
        s_t = s_time / random.randint(1, 100)
        old_text += character
        typing_text = old_text + typing_symbol

        try:
            await message.edit(typing_text)
            time.sleep(s_t)

            await message.edit(old_text)
            time.sleep(s_t)

        except FloodWait as x:
            time.sleep(x.x)