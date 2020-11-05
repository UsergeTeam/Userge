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
    'flags': {
        '-u': "get user_id from replied message",
        '-l': "message limit : max 100"},
    'usage': "reply {tr}purge to the start message to purge.\n"
             "use {tr}purge [user_id | user_name] to purge messages from that user or use flags",
    'examples': ['{tr}purge', '{tr}purge -u', '{tr}purge [user_id | user_name]']},
    allow_bots=False, del_pre=True)
async def purge_(message: Message):
    await message.edit("`purging ...`")
    from_user_id = None
    if message.filtered_input_str:
        from_user_id = (await message.client.get_users(message.filtered_input_str)).id
    start_message = 0
    if 'l' in message.flags:
        limit = min(100, int(message.flags['l']))
        start_message = message.message_id - limit
    if message.reply_to_message:
        start_message = message.reply_to_message.message_id
        if 'u' in message.flags:
            from_user_id = message.reply_to_message.from_user.id
    if not start_message:
        await message.err("invalid start message!")
        return
    list_of_messages = []
    purged_messages_count = 0

    async def handle_msg(a_message):
        nonlocal list_of_messages, purged_messages_count
        if (from_user_id and a_message and a_message.from_user
                and a_message.from_user.id == from_user_id):
            list_of_messages.append(a_message.message_id)
        if not from_user_id:
            list_of_messages.append(a_message.message_id)
        if len(list_of_messages) >= 100:
            await message.client.delete_messages(
                chat_id=message.chat.id,
                message_ids=list_of_messages
            )
            purged_messages_count += len(list_of_messages)
            list_of_messages = []

    start_t = datetime.now()
    if message.client.is_bot:
        for a_message in await message.client.get_messages(
                chat_id=message.chat.id, replies=0,
                message_ids=range(start_message, message.message_id)):
            await handle_msg(a_message)
    else:
        async for a_message in message.client.iter_history(
                chat_id=message.chat.id, limit=None,
                offset_id=start_message, reverse=True):
            await handle_msg(a_message)
    if list_of_messages:
        await message.client.delete_messages(chat_id=message.chat.id,
                                             message_ids=list_of_messages)
        purged_messages_count += len(list_of_messages)
    end_t = datetime.now()
    time_taken_s = (end_t - start_t).seconds
    out = f"<u>purged</u> {purged_messages_count} messages in {time_taken_s} seconds."
    await message.edit(out, del_in=3)
