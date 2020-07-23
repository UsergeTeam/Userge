# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import userge, Message


@userge.on_cmd("ids", about={
    'header': "display ids",
    'usage': "reply {tr}ids any message, file or just send this command"})
async def getids(message: Message):
    replied = message.reply_to_message
    message_id = replied.message_id if replied else message.message_id
    out_str = f"👥 **Chat ID** : `{message.chat.id}`\n💬 **Message ID** : `{message_id}`"
    if message.reply_to_message:
        if message.reply_to_message.from_user:
            out_str += f"\n🙋‍♂️ **From User ID** : `{message.reply_to_message.from_user.id}`"
        file_id = None
        type_ = None
        if message.reply_to_message.media:
            if message.reply_to_message.audio:
                type_ = "audio"
                file_id = message.reply_to_message.audio.file_id
            elif message.reply_to_message.animation:
                type_ = "animation"
                file_id = message.reply_to_message.animation.file_id
            elif message.reply_to_message.document:
                type_ = "document"
                file_id = message.reply_to_message.document.file_id
            elif message.reply_to_message.photo:
                type_ = "photo"
                file_id = message.reply_to_message.photo.file_id
            elif message.reply_to_message.sticker:
                type_ = "sticker"
                file_id = message.reply_to_message.sticker.file_id
            elif message.reply_to_message.voice:
                type_ = "voice"
                file_id = message.reply_to_message.voice.file_id
            elif message.reply_to_message.video_note:
                type_ = "video_note"
                file_id = message.reply_to_message.video_note.file_id
            elif message.reply_to_message.video:
                type_ = "video"
                file_id = message.reply_to_message.video.file_id
            if file_id is not None:
                out_str += f"\n📄 **File ID** (`{type_}`): `{file_id}`"
    await message.edit(out_str)
