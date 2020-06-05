# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Mods']

import asyncio
from typing import Dict, List, Optional, Union

import nest_asyncio
from pyrogram import (
    Client as RawClient, Message as RawMessage,
    InlineKeyboardMarkup, ReplyKeyboardMarkup,
    ReplyKeyboardRemove, ForceReply)
from pyrogram.api import functions

from userge import logging, Config
from .message import Message
from .logger import CLogger
from .conv import Conv
from .. import client as _client

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  :::::  %s  :::::  !>>>"


class Mods(RawClient):
    """some mods for userge"""
    def __init__(self, client: '_client.Userge', **kwargs) -> None:
        super().__init__(**kwargs)
        self._channel = self.getCLogger(__name__)
        Conv.init(client)
        nest_asyncio.apply()

    def getCLogger(self, name: str) -> CLogger:
        """This returns new channel logger object"""
        _LOG.debug(_LOG_STR, f"Creating CLogger => {name}")
        return CLogger(self, name)

    async def get_user_dict(self, user_id: Union[int, str]) -> Dict[str, str]:
        """This will return user `Dict` which contains
        `id`(chat id), `fname`(first name), `lname`(last name),
        `flname`(full name), `uname`(username) and `mention`.
        """
        user_obj = await self.get_users(user_id)
        fname = (user_obj.first_name or '').strip()
        lname = (user_obj.last_name or '').strip()
        username = (user_obj.username or '').strip()
        if fname and lname:
            full_name = fname + ' ' + lname
        elif fname or lname:
            full_name = fname or lname
        else:
            full_name = "user"
        mention = f"[{username or full_name}](tg://user?id={user_id})"
        return {'id': user_obj.id, 'fname': fname, 'lname': lname,
                'flname': full_name, 'uname': username, 'mention': mention}

    def conversation(self,
                     chat_id: Union[str, int],
                     *, timeout: Union[int, float] = 10,
                     limit: int = 10) -> Conv:
        """\nThis returns new conversation object.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages)
                you can simply use "me" or "self".
                For a contact that exists in your Telegram address book
                you can use his phone number (str).

            timeout (``int`` | ``float`` | , *optional*):
                set conversation timeout.
                defaults to 10.

            limit (``int`` | , *optional*):
                set conversation message limit.
                defaults to 10.
        """
        return Conv(self, chat_id, timeout, limit)

    async def send_read_acknowledge(self,
                                    chat_id: Union[int, str],
                                    message: Union[List[RawMessage],
                                                   Optional[RawMessage]] = None,
                                    *, max_id: Optional[int] = None,
                                    clear_mentions: bool = False) -> bool:
        """\nMarks messages as read and optionally clears mentions.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages)
                you can simply use "me" or "self".
                For a contact that exists in your Telegram address book
                you can use his phone number (str).

            message (``list`` | :obj: `Message`, *optional*):
                Either a list of messages or a single message.

            max_id (``int``, *optional*):
                Until which message should the read acknowledge be sent for.
                This has priority over the ``message`` parameter.

            clear_mentions (``bool``, *optional*):
                Whether the mention badge should be cleared (so that
                there are no more mentions) or not for the given entity.
                If no message is provided, this will be the only action
                taken.
                defaults to False.

        Returns:
            On success, True is returned.
        """
        if max_id is None:
            if message:
                if isinstance(message, list):
                    max_id = max(msg.message_id for msg in message)
                else:
                    max_id = message.message_id
            else:
                max_id = 0
        if clear_mentions:
            await self.send(
                functions.messages.ReadMentions(
                    peer=await self.resolve_peer(chat_id)))
            if max_id is None:
                return True
        if max_id is not None:
            return bool(await self.read_history(chat_id=chat_id, max_id=max_id))
        return False

    async def send_message(self,
                           chat_id: Union[int, str],
                           text: str,
                           del_in: int = -1,
                           log: Union[bool, str] = False,
                           parse_mode: Union[str, object] = object,
                           disable_web_page_preview: Optional[bool] = None,
                           disable_notification: Optional[bool] = None,
                           reply_to_message_id: Optional[int] = None,
                           schedule_date: Optional[int] = None,
                           reply_markup: Union[InlineKeyboardMarkup,
                                               ReplyKeyboardMarkup,
                                               ReplyKeyboardRemove,
                                               ForceReply] = None) -> Union[Message, bool]:
        """\nSend text messages.

        Example:
                @userge.send_message(chat_id=12345, text='test')

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages)
                you can simply use "me" or "self".
                For a contact that exists in your Telegram address book
                you can use his phone number (str).

            text (``str``):
                Text of the message to be sent.

            del_in (``int``):
                Time in Seconds for delete that message.

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded to the log channel.
                If ``str``, the logger name will be updated.

            parse_mode (``str``, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            schedule_date (``int``, *optional*):
                Date when the message will be automatically sent. Unix time.

            reply_markup (:obj:`InlineKeyboardMarkup` | :obj:`ReplyKeyboardMarkup`
            | :obj:`ReplyKeyboardRemove` | :obj:`ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard,
                custom reply keyboard, instructions to remove
                reply keyboard or to force a reply from the user.

        Returns:
            :obj:`Message`: On success, the sent text message or True is returned.
        """
        msg = await super().send_message(chat_id=chat_id,
                                         text=text,
                                         parse_mode=parse_mode,
                                         disable_web_page_preview=disable_web_page_preview,
                                         disable_notification=disable_notification,
                                         reply_to_message_id=reply_to_message_id,
                                         schedule_date=schedule_date,
                                         reply_markup=reply_markup)
        if log:
            if isinstance(log, str):
                self._channel.update(log)
            await self._channel.fwd_msg(msg)
        del_in = del_in or Config.MSG_DELETE_TIMEOUT
        if del_in > 0:
            await asyncio.sleep(del_in)
            return await msg.delete()
        return Message(self, msg)
