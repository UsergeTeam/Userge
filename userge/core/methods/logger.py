# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['CLogger']

import asyncio
from typing import Optional, Tuple

from pyrogram import Message as RawMessage
from userge import logging, Config
from userge.utils import SafeDict
from . import message
from .. import client as _client

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  :::::  %s  :::::  !>>>"


class CLogger:
    """ Channel logger for Userge """
    def __init__(self, client: '_client.Userge', name: str) -> None:
        self._client = client
        self._string = self._gen_string(name)

    @staticmethod
    def _gen_string(name: str) -> str:
        return "**logger** : #" + name.split('.')[-1].upper() + "\n\n{}"

    @staticmethod
    def _get_file_id_and_ref(message_: 'message.Message') -> Tuple[str, str]:
        if message_.audio:
            file_ = message_.audio
        elif message_.animation:
            file_ = message_.animation
        elif message_.photo:
            file_ = message_.photo
        elif message_.sticker:
            file_ = message_.sticker
        elif message_.voice:
            file_ = message_.voice
        elif message_.video_note:
            file_ = message_.video_note
        elif message_.video:
            file_ = message_.video
        else:
            file_ = message_.document
        return file_.file_id, file_.file_ref

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

    def update(self, name: str) -> None:
        """\nupdate current logger name.

        Parameters:
            name (``str``):
                New name to logger.

        Returns:
            None
        """
        self._string = self._gen_string(name)

    async def log(self, text: str) -> Optional[int]:
        """\nsend text message to log channel.

        Parameters:
            text (``str``):
                Text of the message to be sent.

        Returns:
            message_id on success or None
        """
        _LOG.debug(_LOG_STR, f"logging text : {text} to channel : {Config.LOG_CHANNEL_ID}")
        if Config.LOG_CHANNEL_ID:
            msg = await self._client.send_message(chat_id=Config.LOG_CHANNEL_ID,
                                                  text=self._string.format(text.strip()))
            return msg.message_id

    async def fwd_msg(self,
                      message_: 'message.Message',
                      as_copy: bool = True,
                      remove_caption: bool = False) -> None:
        """\nforward message to log channel.

        Parameters:
            message_ (`pyrogram.Message`):
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
            _LOG_STR, f"forwarding msg : {message_} to channel : {Config.LOG_CHANNEL_ID}")
        if Config.LOG_CHANNEL_ID and isinstance(message_, RawMessage):
            if message_.media:
                asyncio.get_event_loop().create_task(self.log("**Forwarding Message...**"))
                await self._client.forward_messages(chat_id=Config.LOG_CHANNEL_ID,
                                                    from_chat_id=message_.chat.id,
                                                    message_ids=message_.message_id,
                                                    as_copy=as_copy,
                                                    remove_caption=remove_caption)
            else:
                await self.log(message_.text.html)

    async def store(self,
                    message_: Optional['message.Message'],
                    caption: Optional[str] = '') -> Optional[int]:
        """\nstore message to log channel.

        Parameters:
            message_ (`pyrogram.Message` | `None`):
                pass pyrogram.Message object which want to forward.

            caption (`str`, *optional*):
                Text or Cpation of the message to be sent.

        Returns:
            message_id on success or None
        """
        caption = caption or ''
        if message_ and message_.caption:
            caption = caption + message_.caption.html
        if message_ and message_.media:
            if caption:
                caption = self._string.format(caption.strip())
            file_id, file_ref = self._get_file_id_and_ref(message_)
            msg = await self._client.send_cached_media(chat_id=Config.LOG_CHANNEL_ID,
                                                       file_id=file_id,
                                                       file_ref=file_ref,
                                                       caption=caption)
            message_id = msg.message_id
        else:
            message_id = await self.log(caption)
        return message_id

    async def forward_stored(self,
                             message_id: int,
                             chat_id: int,
                             user_id: int,
                             reply_to_message_id: int,
                             del_in: int = 0) -> None:
        """\nforward stored message from log channel.

        Parameters:
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
            message_id on success or None
        """
        message_ = await self._client.get_messages(chat_id=Config.LOG_CHANNEL_ID,
                                                   message_ids=message_id)
        caption = ''
        if message_.caption:
            caption = message_.caption.html.split('\n\n', maxsplit=1)[-1]
        elif message_.text:
            caption = message_.text.html.split('\n\n', maxsplit=1)[-1]
        if caption:
            u_dict = await self._client.get_user_dict(user_id)
            chat = await self._client.get_chat(chat_id)
            u_dict.update(
                {'chat': chat.title if chat.title else "this group", 'count': chat.members_count})
            caption = caption.format_map(SafeDict(**u_dict))
        if message_.media:
            file_id, file_ref = self._get_file_id_and_ref(message_)
            msg = await self._client.send_cached_media(chat_id=chat_id,
                                                       file_id=file_id,
                                                       file_ref=file_ref,
                                                       caption=caption,
                                                       reply_to_message_id=reply_to_message_id)
        else:
            msg = await self._client.send_message(chat_id=chat_id,
                                                  text=caption,
                                                  reply_to_message_id=reply_to_message_id)
        if del_in and msg:
            await asyncio.sleep(del_in)
            await msg.delete()
