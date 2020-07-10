# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['ChannelLogger']

import re
import asyncio
from typing import Optional, List, Tuple, Union

from pyrogram import Message as RawMessage, InlineKeyboardButton, InlineKeyboardMarkup

from userge import logging, Config
from userge.utils import SafeDict
from ..bound import message as _message  # pylint: disable=unused-import
from ... import client as _client  # pylint: disable=unused-import

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  :::::  %s  :::::  !>>>"
_BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\[buttonurl:(?:/{0,2})(.+?)(:same)?\])")


def _gen_string(name: str) -> str:
    return "**logger** : #" + name.split('.')[-1].upper() + "\n\n{}"


def _get_file_id_and_ref(message: '_message.Message') -> Tuple[Optional[str], Optional[str]]:
    if message.audio:
        file_ = message.audio
    elif message.animation:
        file_ = message.animation
    elif message.photo:
        file_ = message.photo
    elif message.sticker:
        file_ = message.sticker
    elif message.voice:
        file_ = message.voice
    elif message.video_note:
        file_ = message.video_note
    elif message.video:
        file_ = message.video
    else:
        file_ = message.document
    if file_:
        return file_.file_id, file_.file_ref
    return None, None


def _parse_buttons(markdown_note: str):
    prev = 0
    note_data = ""
    buttons: List[Tuple[str, str, str]] = []
    for match in _BTN_URL_REGEX.finditer(markdown_note):
        # Check if btnurl is escaped
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and markdown_note[to_check] == "\\":
            n_escapes += 1
            to_check -= 1
        # if even, not escaped -> create button
        if n_escapes % 2 == 0:
            # create a tuple with button label, url, and newline status
            buttons.append((match.group(2), match.group(3), bool(match.group(4))))
            note_data += markdown_note[prev:match.start(1)]
            prev = match.end(1)
        # if odd, escaped -> move along
        else:
            note_data += markdown_note[prev:to_check]
            prev = match.start(1) - 1
    note_data += markdown_note[prev:]
    return note_data.strip(), _build_keyboard(buttons)


def _build_keyboard(buttons: List[Tuple[str, str, str]]):
    keyb: List[List[InlineKeyboardButton]] = []
    for btn in buttons:
        if btn[2] and keyb:
            keyb[-1].append(InlineKeyboardButton(btn[0], url=btn[1]))
        else:
            keyb.append([InlineKeyboardButton(btn[0], url=btn[1])])
    return keyb


class ChannelLogger:
    """ Channel logger for Userge """
    def __init__(self, client: Union['_client.Userge', '_client._UsergeBot'], name: str) -> None:
        self._client = client
        self._string = _gen_string(name)

    @staticmethod
    def get_link(message_id: int) -> str:
        """\nreturns link for a specific message.

        Parameters:
            message_id (`int`):
                Message id of stored message.

        Returns:
            str
        """
        return "<b><a href='https://t.me/c/{}/{}'>Preview</a></b>".format(
            str(Config.LOG_CHANNEL_ID)[4:], message_id)

    def bind(self, client: Union['_client.Userge', '_client._UsergeBot']) -> None:
        """\nbind with new client

        Parameters:
            client (`Userge` | `usergeBot`):
                Pass Userge or UsergeBot.

        Returns:
            None
        """
        self._client = client

    def update(self, name: str) -> None:
        """\nupdate current logger name.

        Parameters:
            name (``str``):
                New name to logger.

        Returns:
            None
        """
        self._string = _gen_string(name)

    async def log(self, text: str) -> int:
        """\nsend text message to log channel.

        Parameters:
            text (``str``):
                Text of the message to be sent.

        Returns:
            message_id on success or None
        """
        _LOG.debug(_LOG_STR, f"logging text : {text} to channel : {Config.LOG_CHANNEL_ID}")
        msg = await self._client.send_message(chat_id=Config.LOG_CHANNEL_ID,
                                              text=self._string.format(text.strip()))
        return msg.message_id

    async def fwd_msg(self,
                      message: '_message.Message',
                      as_copy: bool = True,
                      remove_caption: bool = False) -> None:
        """\nforward message to log channel.

        Parameters:
            message (`pyrogram.Message`):
                pass pyrogram.Message object which want to forward.

            as_copy (`bool`, *optional*):
                Pass True to forward messages without the forward header
                (i.e.: send a copy of the message content so
                that it appears as originally sent by you).
                Defaults to True.

            remove_caption (`bool`, *optional*):
                If set to True and *as_copy* is enabled as well,
                media captions are not preserved when copying the
                message. Has no effect if *as_copy* is not enabled.
                Defaults to False.

        Returns:
            None
        """
        _LOG.debug(
            _LOG_STR, f"forwarding msg : {message} to channel : {Config.LOG_CHANNEL_ID}")
        if isinstance(message, RawMessage):
            if message.media:
                asyncio.get_event_loop().create_task(self.log("**Forwarding Message...**"))
                await self._client.forward_messages(chat_id=Config.LOG_CHANNEL_ID,
                                                    from_chat_id=message.chat.id,
                                                    message_ids=message.message_id,
                                                    as_copy=as_copy,
                                                    remove_caption=remove_caption)
            else:
                await self.log(
                    message.text.html if hasattr(message.text, 'html') else message.text)

    async def store(self,
                    message: Optional['_message.Message'],
                    caption: Optional[str] = '') -> int:
        """\nstore message to log channel.

        Parameters:
            message (`pyrogram.Message` | `None`):
                pass pyrogram.Message object which want to forward.

            caption (`str`, *optional*):
                Text or Cpation of the message to be sent.

        Returns:
            message_id on success or None
        """
        caption = caption or ''
        file_id = file_ref = None
        if message and message.caption:
            caption = caption + message.caption.html
        if message:
            file_id, file_ref = _get_file_id_and_ref(message)
        if message and message.media and file_id and file_ref:
            if caption:
                caption = self._string.format(caption.strip())
            msg = await self._client.send_cached_media(chat_id=Config.LOG_CHANNEL_ID,
                                                       file_id=file_id,
                                                       file_ref=file_ref,
                                                       caption=caption)
            message_id = msg.message_id
        else:
            message_id = await self.log(caption)
        return message_id

    async def forward_stored(self,
                             client: Union['_client.Userge', '_client._UsergeBot'],
                             message_id: int,
                             chat_id: int,
                             user_id: int,
                             reply_to_message_id: int,
                             del_in: int = 0) -> None:
        """\nforward stored message from log channel.

        Parameters:
            client (`Userge` | `usergeBot`):
                Pass Userge or UsergeBot.

            message_id (`int`):
                Message id of stored message.

            chat_id (`int`):
                ID of chat (dest) you want to farward.

            user_id (`int`):
                ID of user you want to reply.

            reply_to_message_id (`int`):
                If the message is a reply, ID of the original message.

            del_in (`int`):
                Time in Seconds for delete that message.

        Returns:
            None
        """
        if message_id and isinstance(message_id, int):
            message = await client.get_messages(chat_id=Config.LOG_CHANNEL_ID,
                                                message_ids=message_id)
            caption = ''
            file_id = file_ref = None
            if message.caption:
                caption = message.caption.html.split('\n\n', maxsplit=1)[-1]
            elif message.text:
                caption = message.text.html.split('\n\n', maxsplit=1)[-1]
            if caption:
                u_dict = await client.get_user_dict(user_id)
                chat = await client.get_chat(chat_id)
                u_dict.update({
                    'chat': chat.title if chat.title else "this group",
                    'count': chat.members_count})
                caption = caption.format_map(SafeDict(**u_dict))
            file_id, file_ref = _get_file_id_and_ref(message)
            caption, buttons = _parse_buttons(caption)
            if message.media and file_id and file_ref:
                msg = await client.send_cached_media(
                    chat_id=chat_id,
                    file_id=file_id,
                    file_ref=file_ref,
                    caption=caption,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=InlineKeyboardMarkup(buttons)
                    if hasattr(client, 'ubot') and buttons else None)
            else:
                msg = await client.send_message(
                    chat_id=chat_id,
                    text=caption,
                    reply_to_message_id=reply_to_message_id,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(buttons)
                    if hasattr(client, 'ubot') and buttons else None)
            if del_in and msg:
                await asyncio.sleep(del_in)
                await msg.delete()
