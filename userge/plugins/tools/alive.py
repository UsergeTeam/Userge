# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram.errors.exceptions import FileIdInvalid, FileReferenceEmpty
from pyrogram.errors.exceptions.bad_request_400 import BadRequest, ChannelInvalid, MediaEmpty

from userge.core.ext import RawClient
from userge import userge, Message, Config, versions, get_version

LOGO_STICKER_ID, LOGO_STICKER_REF = None, None


@userge.on_cmd("alive", about={
    'header': "This command is just for fun"}, allow_channels=False)
async def alive(message: Message):
    await message.delete()
    await sendit(message)
    output = f"""
**uptime** : `{userge.uptime}`
**version** : `{get_version()}`

• **sudo** : `{_parse_arg(Config.SUDO_ENABLED)}`
• **antispam** : `{_parse_arg(Config.ANTISPAM_SENTRY)}`
• **dualmode** : `{_parse_arg(RawClient.DUAL_MODE)}`
• **unofficial** : `{_parse_arg(Config.LOAD_UNOFFICIAL_PLUGINS)}`

    **__python__** : `{versions.__python_version__}`
    **__pyrogram__** : `{versions.__pyro_version__}`

**{versions.__license__}** | **{versions.__copyright__}** | **[Repo]({Config.UPSTREAM_REPO})**
"""
    await message.client.send_message(message.chat.id, output, disable_web_page_preview=True)


def _parse_arg(arg: bool) -> str:
    return "enabled" if arg else "disabled"


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
