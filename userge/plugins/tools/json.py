from userge import userge, Message, Config


@userge.on_cmd("json", about="""\
__message object to json__

**Usage:**

    reply `.json` to any message""")
async def jsonify(message: Message):
    the_real_message = str(message.reply_to_message) if message.reply_to_message \
        else str(message)

    if len(the_real_message) > Config.MAX_MESSAGE_LENGTH:
        await message.send_as_file(text=the_real_message,
                                   filename="json.txt",
                                   caption="Too Large")

    else:
        await message.edit(the_real_message)
