from userge import userge, Message
from userge.utils import CANCEL_LIST


@userge.on_cmd("cancel", about="\
__Reply this to message you want to cancel__")
async def cancel_(message: Message):
    replied = message.reply_to_message

    if replied:
        CANCEL_LIST.append(replied.message_id)
        await message.edit(
            "`added your request to cancel list`", del_in=5)

    else:
        await message.edit(
            "`reply to the message you want to cancel`", del_in=5)
