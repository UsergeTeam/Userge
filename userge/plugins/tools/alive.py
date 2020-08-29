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

LOGO_ID, LOGO_REF = None, None


@userge.on_cmd("alive", about={
    'header': "This command is just for fun"}, allow_channels=False)
async def alive(message: Message):
    await message.delete()
    try:
        await sendit(message.chat.id)
    except (FileIdInvalid, FileReferenceEmpty, BadRequest):
        await refresh_id()
        await sendit(message.chat.id)


def _parse_arg(arg: bool) -> str:
    return "✓" if arg else "X"


async def refresh_id():
    global LOGO_ID, LOGO_REF  # pylint: disable=global-statement
    gif = (await userge.get_messages('UserGeOt', 511623)).animation
    LOGO_ID = gif.file_id
    LOGO_REF = gif.file_ref


async def sendit(message):
    if not LOGO_ID:
        try:
            await refresh_id()
        except ChannelInvalid:
            pass
    output = f"""
**⌚️ Uptime** : `{userge.uptime}`
**💥 Version** : `{get_version()}`

• **Sudo**: `{_parse_arg(Config.SUDO_ENABLED)}`
• **Anti-Spam**: `{_parse_arg(Config.ANTISPAM_SENTRY)}`
• **Dual-Mode**: `{_parse_arg(RawClient.DUAL_MODE)}`
"""
    if Config.HEROKU_APP:
        output += f"• **Dyno-Saver**: `{_parse_arg(Config.RUN_DYNO_SAVER)}`"
    output += f"""
• **unofficial**: `{_parse_arg(Config.LOAD_UNOFFICIAL_PLUGINS)}`

    **__Python__**: `{versions.__python_version__}`
    **__Pyrogram__**: `{versions.__pyro_version__}`

**{versions.__license__}** | **{versions.__copyright__}** | **[Repo]({Config.UPSTREAM_REPO})**
"""
    try:
        await message.reply_animation(
            LOGO_ID, file_ref=LOGO_REF, caption=output)
    except MediaEmpty:
        pass
