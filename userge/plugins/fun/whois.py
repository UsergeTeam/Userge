# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os

from pyrogram.errors.exceptions.bad_request_400 import BotMethodInvalid

from userge import userge, Message


@userge.on_cmd("whois", about={
    'header': "use this to get any user details",
    'usage': "just reply to any user message or add user_id or username",
    'examples': "{tr}whois [user_id | username]"}, allow_channels=False)
async def who_is(message: Message):
    await message.edit("`Collecting Whois Info.. Hang on!`")
    user_id = message.input_str
    if user_id:
        try:
            from_user = await message.client.get_users(user_id)
            from_chat = await message.client.get_chat(user_id)
        except Exception:
            await message.err(
                "no valid user_id or message specified, do .help whois for more info")
            return
    elif message.reply_to_message:
        from_user = await message.client.get_users(message.reply_to_message.from_user.id)
        from_chat = await message.client.get_chat(message.reply_to_message.from_user.id)
    else:
        await message.err("no valid user_id or message specified, do .help whois for more info")
        return
    if from_user or from_chat is not None:
        pp_c = await message.client.get_profile_photos_count(from_user.id)
        message_out_str = "<b>USER INFO:</b>\n\n"
        message_out_str += f"<b>🗣 First Name:</b> <code>{from_user.first_name}</code>\n"
        message_out_str += f"<b>🗣 Last Name:</b> <code>{from_user.last_name}</code>\n"
        message_out_str += f"<b>👤 Username:</b> @{from_user.username}\n"
        message_out_str += f"<b>🏢 DC ID:</b> <code>{from_user.dc_id}</code>\n"
        message_out_str += f"<b>🤖 Is Bot:</b> <code>{from_user.is_bot}</code>\n"
        message_out_str += f"<b>🚫 Is Restricted:</b> <code>{from_user.is_scam}</code>\n"
        message_out_str += "<b>✅ Is Verified by Telegram:</b> "
        message_out_str += f"<code>{from_user.is_verified}</code>\n"
        message_out_str += f"<b>🕵️‍♂️ User ID:</b> <code>{from_user.id}</code>\n"
        message_out_str += f"<b>🖼 Profile Photos:</b> <code>{pp_c}</code>\n"
        try:
            cc_no = len(await message.client.get_common_chats(from_user.id))
        except BotMethodInvalid:
            pass
        else:
            message_out_str += f"<b>👥 Common Chats:</b> <code>{cc_no}</code>\n"
        message_out_str += f"<b>📝 Bio:</b> <code>{from_chat.bio}</code>\n\n"
        message_out_str += f"<b>👁 Last Seen:</b> <code>{from_user.status}</code>\n"
        message_out_str += "<b>🔗 Permanent Link To Profile:</b> "
        message_out_str += f"<a href='tg://user?id={from_user.id}'>{from_user.first_name}</a>"

        s_perm = True
        if message.chat.permissions:
            s_perm = bool(message.chat.permissions.can_send_media_messages)
        if from_user.photo and s_perm:
            local_user_photo = await message.client.download_media(
                message=from_user.photo.big_file_id)
            await message.client.send_photo(chat_id=message.chat.id,
                                            photo=local_user_photo,
                                            caption=message_out_str,
                                            parse_mode="html",
                                            disable_notification=True)
            os.remove(local_user_photo)
            await message.delete()
        else:
            cuz = "NO DP Found"
            if not s_perm:
                cuz = "Chat Send Media Forbidden"
            message_out_str = "<b>📷 " + cuz + " 📷</b>\n\n" + message_out_str
            await message.edit(message_out_str)
