# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from datetime import datetime

from userge import userge, Message


@userge.on_cmd("purge", about={
    'header': "purge messages from user",
    'flags': {'-u': "get user_id from replied message"},
    'usage': "reply {tr}purge to the start message to purge.\n"
             "use {tr}purge [user_id | user_name] to purge messages from that user or use flags",
    'examples': ['{tr}purge', '{tr}purge -u', '{tr}purge [user_id | user_name]']})
async def purge_(message: Message):
    if message.reply_to_message:
        start_t = datetime.now()
        user_id = message.filtered_input_str
        flags = message.flags
        if '-u' in flags:
            from_user = message.reply_to_message.from_user
        elif user_id:
            from_user = await userge.get_users(user_id)
        else:
            from_user = None
        start_message = message.reply_to_message.message_id
        end_message = message.message_id

        list_of_messages = await userge.get_messages(chat_id=message.chat.id,
                                                     message_ids=range(start_message, end_message),
                                                     replies=0)
        list_of_messages_to_delete = []
        purged_messages_count = 0
        for a_message in list_of_messages:
            if len(list_of_messages_to_delete) == 100:
                await userge.delete_messages(chat_id=message.chat.id,
                                             message_ids=list_of_messages_to_delete,
                                             revoke=True)

                purged_messages_count += len(list_of_messages_to_delete)
                list_of_messages_to_delete = []
            if from_user is not None:
                if a_message.from_user == from_user:
                    list_of_messages_to_delete.append(a_message.message_id)
            else:
                list_of_messages_to_delete.append(a_message.message_id)
        await userge.delete_messages(chat_id=message.chat.id,
                                     message_ids=list_of_messages_to_delete,
                                     revoke=True)
        purged_messages_count += len(list_of_messages_to_delete)
        end_t = datetime.now()
        time_taken_s = (end_t - start_t).seconds
        out = f"<u>purged</u> {purged_messages_count} messages in {time_taken_s} seconds."
        await message.edit(text=out, del_in=3)
    else:
        out = "Reply to a message to purge [user's] messages."
        await message.err(text=out)
