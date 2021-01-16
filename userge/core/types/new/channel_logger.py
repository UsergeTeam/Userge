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

import asyncio
from typing import Optional, Union

from pyrogram.errors import ChatWriteForbidden
from pyrogram.types import Message as RawMessage
from pyrogram.errors.exceptions import MessageTooLong

from userge import logging, Config
from userge.utils import SafeDict, get_file_id_of_media, parse_buttons
from ..bound import message as _message  # pylint: disable=unused-import
from ... import client as _client  # pylint: disable=unused-import

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  :::::  %s  :::::  !>>>"


def _gen_string(name: str) -> str:
    return "**logger** : #" + name.split('.')[-1].upper() + "\n\n{}"


class ChannelLogger:
    """ Channel logger for Userge """
    def __init__(self, client: Union['_client.Userge', '_client.UsergeBot'], name: str) -> None:
        self._id = Config.LOG_CHANNEL_ID
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

    async def log(self, text: str, name: str = '') -> int:
        """\nsend text message to log channel.

        Parameters:
            text (``str``):
                Text of the message to be sent.

            name (``str``, *optional*):
                New Name for logger.

        Returns:
            message_id on success or None
        """
        string = self._string
        if name:
            string = _gen_string(name)
        _LOG.debug(_LOG_STR, f"logging text : {text} to channel : {self._id}")
        try:
            msg = await self._client.send_message(chat_id=self._id,
                                                  text=string.format(text.strip()))
        except MessageTooLong:
            msg = await self._client.send_as_file(chat_id=self._id,
                                                  text=string.format(text.strip()),
                                                  filename="logs.log",
                                                  caption=string)
        return msg.message_id

    async def fwd_msg(self,
                      message: Union['_message.Message', 'RawMessage'],
                      name: str = '',
                      as_copy: bool = True) -> None:
        """\nforward message to log channel.

        Parameters:
            message (`pyrogram.Message`):
                pass pyrogram.Message object which want to forward.

            name (``str``, *optional*):
                New Name for logger.

            as_copy (`bool`, *optional*):
                Pass True to forward messages without the forward header
                (i.e.: send a copy of the message content so
                that it appears as originally sent by you).
                Defaults to True.

        Returns:
            None
        """
        _LOG.debug(
            _LOG_STR, f"forwarding msg : {message} to channel : {self._id}")
        if isinstance(message, RawMessage):
            if message.media:
                asyncio.get_event_loop().create_task(self.log("**Forwarding Message...**", name))
                try:
                    if as_copy:
                        await message.copy(chat_id=self._id)
                    else:
                        await message.forward(chat_id=self._id)
                except ValueError:
                    pass
            else:
                await self.log(
                    message.text.html if hasattr(message.text, 'html') else message.text, name)

    async def store(self,
                    message: Optional['_message.Message'],
                    caption: Optional[str] = '') -> int:
        """\nstore message to log channel.

        Parameters:
            message (`pyrogram.Message` | `None`):
                pass pyrogram.Message object which want to forward.

            caption (`str`, *optional*):
                Text or Caption of the message to be sent.

        Returns:
            message_id on success or None
        """
        caption = caption or ''
        file_id = None
        if message and message.caption:
            caption = caption + message.caption.html
        if message:
            file_id = get_file_id_of_media(message)
        if message and message.media and file_id:
            if caption:
                caption = self._string.format(caption.strip())
            msg = await message.client.send_cached_media(chat_id=self._id,
                                                         file_id=file_id,
                                                         caption=caption)
            message_id = msg.message_id
        else:
            message_id = await self.log(caption)
        return message_id

    async def forward_stored(self,
                             client: Union['_client.Userge', '_client.UsergeBot'],
                             message_id: int,
                             chat_id: int,
                             user_id: int,
                             reply_to_message_id: int,
                             del_in: int = 0) -> None:
        """\nforward stored message from log channel.

        Parameters:
            client (`Userge` | `UsergeBot`):
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
        if not message_id or not isinstance(message_id, int):
            return
        message = await client.get_messages(chat_id=self._id,
                                            message_ids=message_id)
        caption = ''
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
        file_id = get_file_id_of_media(message)
        caption, buttons = parse_buttons(caption)
        try:
            if message.media and file_id:
                msg = await client.send_cached_media(
                    chat_id=chat_id,
                    file_id=file_id,
                    caption=caption,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=buttons if client.is_bot and buttons else None)
            else:
                msg = await client.send_message(
                    chat_id=chat_id,
                    text=caption,
                    reply_to_message_id=reply_to_message_id,
                    disable_web_page_preview=True,
                    reply_markup=buttons if client.is_bot and buttons else None)
            if del_in and msg:
                await asyncio.sleep(del_in)
                await msg.delete()
        except ChatWriteForbidden:
            pass
