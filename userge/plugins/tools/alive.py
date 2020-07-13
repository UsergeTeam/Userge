# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram.errors.exceptions import FileIdInvalid, FileReferenceEmpty
from pyrogram.errors.exceptions.bad_request_400 import BadRequest, ChannelInvalid, MediaEmpty

from userge import userge, Message, Config, versions, get_version

LOGO_STICKER_ID, LOGO_STICKER_REF = None, None


@userge.on_cmd("alive", about={
    'header': "This command is just for fun"}, allow_channels=False)
async def alive(message: Message):
    await message.delete()
    await sendit(message)
    output = f"""
**USERGE is Up and Running**

       __Durable as a Serge__

• **uptime** : `{userge.uptime}`
• **python version** : `{versions.__python_version__}`
• **pyrogram version** : `{versions.__pyro_version__}`
• **userge version** : `{get_version()}`
• **license** : {versions.__license__}
• **copyright** : {versions.__copyright__}
• **repo** : [Userge]({Config.UPSTREAM_REPO})
"""
    await message.client.send_message(message.chat.id, output, disable_web_page_preview=True)


async def refresh_id():
    global LOGO_STICKER_ID, LOGO_STICKER_REF  # pylint: disable=global-statement
    sticker = (await userge.get_messages('theUserge', 8)).sticker
    LOGO_STICKER_ID = sticker.file_id
    LOGO_STICKER_REF = sticker.file_ref


async def send_sticker(message):
    try:
        await message.client.send_sticker(
            message.chat.id, LOGO_STICKER_ID, file_ref=LOGO_STICKER_REF)
    except MediaEmpty:
        pass


async def sendit(message):
    if LOGO_STICKER_ID:
        try:
            await send_sticker(message)
        except (FileIdInvalid, FileReferenceEmpty, BadRequest):
            try:
                await refresh_id()
            except ChannelInvalid:
                pass
            else:
                await send_sticker(message)
    else:
        try:
            await refresh_id()
        except ChannelInvalid:
            pass
        else:
            await send_sticker(message)
