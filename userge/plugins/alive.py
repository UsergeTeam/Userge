from userge import userge
from pyrogram.errors.exceptions import FileIdInvalid

LOGO_STICKER_ID = None


@userge.on_cmd("alive", about="__This command is just for fun XD__")
async def alive(_, message):
    await message.delete()

    try:
        if LOGO_STICKER_ID:
            await sendit(LOGO_STICKER_ID, message)

        else:
            await refresh_id()
            await sendit(LOGO_STICKER_ID, message)
            
    except FileIdInvalid:
        await refresh_id()
        await sendit(LOGO_STICKER_ID, message)

    await userge.send_message(message.chat.id, "`USERGE is Up and Running`")


async def refresh_id():
    global LOGO_STICKER_ID
    LOGO_STICKER_ID = (await userge.get_messages('theUserge', 8)).sticker.file_id


async def sendit(fileid, message):
    await userge.send_sticker(message.chat.id, fileid)
