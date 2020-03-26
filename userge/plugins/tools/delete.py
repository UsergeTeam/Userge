from userge import userge, Message


@userge.on_cmd("del", about="__delete replied message__")
async def del_msg(message: Message):
    msg_ids = [message.message_id]

    if message.reply_to_message:
        msg_ids.append(message.reply_to_message.message_id)

    await userge.delete_messages(message.chat.id, msg_ids)
