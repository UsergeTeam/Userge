# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
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

    async def handle_msg(_msg):
        nonlocal list_of_messages, purged_messages_count
        if (from_user_id and _msg and _msg.from_user
                and _msg.from_user.id == from_user_id):
            list_of_messages.append(_msg.message_id)
        if not from_user_id:
            list_of_messages.append(_msg.message_id)
        if len(list_of_messages) >= 100:
            await message.client.delete_messages(
                chat_id=message.chat.id,
                message_ids=list_of_messages
            )
            purged_messages_count += len(list_of_messages)
            list_of_messages = []

    start_t = datetime.now()
    if message.client.is_bot:
        for msg in await message.client.get_messages(
                chat_id=message.chat.id, replies=0,
                message_ids=range(start_message, message.message_id)):
            await handle_msg(msg)
    else:
        async for msg in message.client.iter_history(
                chat_id=message.chat.id, offset_id=start_message, reverse=True):
            await handle_msg(msg)
    if list_of_messages:
        await message.client.delete_messages(chat_id=message.chat.id,
                                             message_ids=list_of_messages)
        purged_messages_count += len(list_of_messages)
    end_t = datetime.now()
    time_taken_s = (end_t - start_t).seconds
    out = f"<u>purged</u> {purged_messages_count} messages in {time_taken_s} seconds."
    await message.edit(out, del_in=3)


@userge.on_cmd("del", about={'header': "delete replied message"})
async def del_msg(message: Message):
    if userge.dual_mode:
        u_msg_ids = []
        b_msg_ids = []
        o_msg_ids = []
        for m in filter(lambda _: _, (message, message.reply_to_message)):
            if m.from_user and m.from_user.id == userge.id:
                u_msg_ids.append(m.message_id)
            elif m.from_user and m.from_user.id == userge.bot.id:
                b_msg_ids.append(m.message_id)
            else:
                o_msg_ids.append(m.message_id)
        if u_msg_ids:
            await userge.delete_messages(message.chat.id, u_msg_ids)
        if b_msg_ids:
            await userge.bot.delete_messages(message.chat.id, b_msg_ids)
        for o_msg_id in o_msg_ids:
            try:
                await userge.delete_messages(message.chat.id, o_msg_id)
            except MessageDeleteForbidden:
                try:
                    await userge.bot.delete_messages(message.chat.id, o_msg_id)
                except MessageDeleteForbidden:
                    pass
    else:
        await message.delete()
        replied = message.reply_to_message
        if replied:
            await replied.delete()
