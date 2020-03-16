import os
from pyrogram import Message
from userge import userge

log = userge.getLogger(__name__)


@userge.on_cmd("json")
async def jsonify(_, message: Message):
    the_real_message = None
    reply_to_id =  None

    if message.reply_to_message:
        reply_to_id = message.reply_to_message.message_id
        the_real_message = message.reply_to_message
    else:
        the_real_message = message
        reply_to_id = message.message_id

    try:
        await message.edit(the_real_message)
    except Exception as e:
        with open("json.text", "w+", encoding="utf8") as out_file:
            out_file.write(str(the_real_message))
        await userge.send_document(
            chat_id=message.chat.id,
            document="json.text",
            caption=str(e),
            disable_notification=True,
            reply_to_message_id=reply_to_id
        )
        os.remove("json.text")
        await message.delete()


userge.add_help(
    command="json",
    about="replied msg to json"
)