import asyncio

from pyrogram.errors.exceptions.bad_request_400 import YouBlockedUser

from userge import userge, Message


@userge.on_cmd("deepifry", about={
    'header': " Deepfrying media",
    'usage': "{tr}deepifry [lvl from 1 to 8] [reply to media]",
    'examples': "{tr}deepifry 3 [reply to media]"})
async def deepifry_(message: Message):
    """ deepfry any media """
    replied = message.reply_to_message
    if not replied:
       await message.err("```Reply to Media to deepfry !...```", del_in=5)
       return
    if not replied.media:
       await message.err("```Reply to Media only !...```", del_in=5)
       return

    uploaded_gif = None
    chat = "@Image_DeepfryBot"
    await message.edit("```Deepfrying, Wait plox ...```", del_in=3)
    

    async with userge.conversation(chat) as conv:
        try:
            await conv.send_message("/start")
        except YouBlockedUser:
            await message.edit("**For your kind information, you blocked @Image_DeepfryBot, Unblock it**", del_in=5)
            return
        await conv.get_response(mark_read=True)
        await conv.forward_message(replied)
        response = await conv.get_response(mark_read=True)
        
        if not response.sticker:
            await message.err('```Bot is Down, try to restart Bot !...```')
        else:
            message_id = replied.message_id if replied else None
            await userge.send_sticker(chat_id=message.chat.id,
                                  sticker=response.sticker.file_id,
                                  file_ref=response.sticker.file_ref,
                                  reply_to_message_id=message_id)