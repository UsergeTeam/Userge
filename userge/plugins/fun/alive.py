# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from pyrogram.errors.exceptions import FileIdInvalid, FileReferenceEmpty
from userge import userge, Message, Config, versions

LOGO_STICKER_ID, LOGO_STICKER_REF = None, None


@userge.on_cmd("alive", about="__This command is just for fun XD__")
async def alive(message: Message):
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

    except FileReferenceEmpty:
        await refresh_id()
        await sendit(LOGO_STICKER_ID, message)

    output = f"""
**USERGE is Up and Running**

• **python version** : `{versions.__python_version__}`
• **pyrogram version** : `{versions.__pyro_version__}`
• **userge version** : `{versions.__version__}`
• **license** : {versions.__license__}
• **copyright** : {versions.__copyright__}
• **repo** : [Userge]({Config.UPSTREAM_REPO})
"""

    await userge.send_message(message.chat.id, output)


async def refresh_id():
    global LOGO_STICKER_ID, LOGO_STICKER_REF
    sticker = (await userge.get_messages('theUserge', 8)).sticker
    LOGO_STICKER_ID = sticker.file_id
    LOGO_STICKER_REF = sticker.file_ref


async def sendit(fileid, message):
    await userge.send_sticker(message.chat.id, fileid, file_ref=LOGO_STICKER_REF)
