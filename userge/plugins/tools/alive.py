# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import re
import asyncio
from typing import Tuple, Optional

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ChatSendMediaForbidden, Forbidden, SlowmodeWait, PeerIdInvalid,
    FileIdInvalid, FileReferenceEmpty, BadRequest, ChannelInvalid, MediaEmpty
)

from userge.core.ext import RawClient
from userge.utils import get_file_id_and_ref
from userge import userge, Message, Config, versions, get_version, logging

_LOG = logging.getLogger(__name__)

_IS_TELEGRAPH = False
_IS_STICKER = False

_DEFAULT = "https://t.me/theUserge/31"
_CHAT, _MSG_ID = None, None
_LOGO_ID, _LOGO_REF = None, None


@userge.on_cmd("alive", about={
    'header': "This command is just for fun"}, allow_channels=False)
async def alive(message: Message):
    if not (_CHAT and _MSG_ID):
        try:
            _set_data()
        except Exception as set_err:
            _LOG.exception("There was some problem while setting Media Data. "
                           f"trying again... ERROR:: {set_err} ::")
            _set_data(True)

    alive_text, markup = _get_alive_text_and_markup(message)
    if _MSG_ID == "text_format":
        return await message.edit(alive_text, disable_web_page_preview=True, reply_markup=markup)
    await message.delete()
    try:
        await _send_alive(message, alive_text, markup)
    except (FileIdInvalid, FileReferenceEmpty, BadRequest):
        await _refresh_id(message)
        await _send_alive(message, alive_text, markup)


def _get_mode() -> str:
    if RawClient.DUAL_MODE:
        return "Dual"
    if Config.BOT_TOKEN:
        return "Bot"
    return "User"


def _get_alive_text_and_markup(message: Message) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
    markup = None
    output = f"""
**⏱ Uptime** : `{userge.uptime}`
**💡 Version** : `{get_version()}`
**⚙️ Mode** : `{_get_mode().upper()}`

• **Sudo**: `{_parse_arg(Config.SUDO_ENABLED)}`
• **Pm-Guard**: `{_parse_arg(not Config.ALLOW_ALL_PMS)}`
• **Anti-Spam**: `{_parse_arg(Config.ANTISPAM_SENTRY)}`"""
    if Config.HEROKU_APP:
        output += f"\n• **Dyno-saver**: `{_parse_arg(Config.RUN_DYNO_SAVER)}`"
    output += f"""
• **Unofficial**: `{_parse_arg(Config.LOAD_UNOFFICIAL_PLUGINS)}`

    **__Python__**: `{versions.__python_version__}`
    **__Pyrogram__**: `{versions.__pyro_version__}`"""
    if not message.client.is_bot:
        output += f"""\n
🎖 **{versions.__license__}** | 👥 **{versions.__copyright__}** | 🧪 **[Repo]({Config.UPSTREAM_REPO})**
"""
    else:
        copy_ = "https://github.com/UsergeTeam/Userge/blob/master/LICENSE"
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="👥 UsergeTeam", url="https://github.com/UsergeTeam"),
                InlineKeyboardButton(text="🧪 Repo", url=Config.UPSTREAM_REPO)
            ],
            [InlineKeyboardButton(text="🎖 GNU GPL v3.0", url=copy_)]
        ])
    return (output, markup)


def _parse_arg(arg: bool) -> str:
    return "enabled" if arg else "disabled"


async def _send_alive(message: Message,
                      text: str,
                      reply_markup: Optional[InlineKeyboardMarkup],
                      recurs_count: int = 0) -> None:
    if not (_LOGO_ID and _LOGO_REF):
        await _refresh_id(message)
    should_mark = None if _IS_STICKER else reply_markup
    if _IS_TELEGRAPH:
        try:
            await message.client.send_document(chat_id=message.chat.id,
                                               document=Config.ALIVE_MEDIA,
                                               caption=text,
                                               reply_markup=should_mark)
        except SlowmodeWait as s_m:
            await asyncio.sleep(s_m.x)
            text = f'<b>{str(s_m).replace(" is ", " was ")}</b>\n\n{text}'
            return await _send_alive(message, text, reply_markup)
        except Exception:
            _LOG.error('Telegraph Link Invalid')
            _set_data(True)
    else:
        try:
            await message.client.send_cached_media(chat_id=message.chat.id,
                                                   file_id=_LOGO_ID,
                                                   file_ref=_LOGO_REF,
                                                   caption=text,
                                                   reply_markup=should_mark)
            if _IS_STICKER:
                raise ChatSendMediaForbidden
        except SlowmodeWait as s_m:
            await asyncio.sleep(s_m.x)
            text = f'<b>{str(s_m).replace(" is ", " was ")}</b>\n\n{text}'
            return await _send_alive(message, text, reply_markup)
        except MediaEmpty:
            if recurs_count >= 2:
                raise ChatSendMediaForbidden
            await _refresh_id(message)
            return await _send_alive(message, text, reply_markup, recurs_count + 1)
        except (ChatSendMediaForbidden, Forbidden):
            await message.client.send_message(chat_id=message.chat.id,
                                              text=text,
                                              disable_web_page_preview=True,
                                              reply_markup=should_mark)


async def _refresh_id(message: Message) -> None:
    global _LOGO_ID, _LOGO_REF, _IS_STICKER  # pylint: disable=global-statement
    try:
        media = await message.client.get_messages(_CHAT, _MSG_ID)
    except (ChannelInvalid, PeerIdInvalid, ValueError):
        _set_data(True)
        return await _refresh_id(message)
    else:
        if media.sticker:
            _IS_STICKER = True
        _LOGO_ID, _LOGO_REF = get_file_id_and_ref(media)


def _set_data(errored: bool = False) -> None:
    global _CHAT, _MSG_ID, _IS_TELEGRAPH  # pylint: disable=global-statement

    pattern_1 = r"^(http(?:s?):\/\/)?(www\.)?(t.me)(\/c\/(\d+)|:?\/(\w+))?\/(\d+)$"
    pattern_2 = r"^(http(?:s?):\/\/)?(www\.)?telegra\.ph\/([A-Za-z0-9\-]*)$"
    if Config.ALIVE_MEDIA and not errored:
        if Config.ALIVE_MEDIA.lower().strip() == "nothing":
            _CHAT = "text_format"
            _MSG_ID = "text_format"
            return
        media_link = Config.ALIVE_MEDIA
        match_1 = re.search(pattern_1, media_link)
        match_2 = re.search(pattern_2, media_link)
        if match_1:
            _MSG_ID = int(match_1.group(7))
            if match_1.group(5):
                _CHAT = int("-100" + match_1.group(5))
            elif match_1.group(6):
                _CHAT = match_1.group(6)
        elif match_2:
            _IS_TELEGRAPH = True
        elif "|" in Config.ALIVE_MEDIA:
            _CHAT, _MSG_ID = Config.ALIVE_MEDIA.split("|", maxsplit=1)
            _CHAT = _CHAT.strip()
            _MSG_ID = int(_MSG_ID.strip())
    else:
        match = re.search(pattern_1, _DEFAULT)
        _CHAT = match.group(6)
        _MSG_ID = int(match.group(7))
