# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['SendMessage']

import asyncio
import inspect
from datetime import datetime
from typing import Optional, Union, List

from pyrogram.types import (
    InlineKeyboardMarkup, ReplyKeyboardMarkup,
    ReplyKeyboardRemove, ForceReply, MessageEntity)
from pyrogram import enums

from userge import config
from ... import types
from ...ext import RawClient


class SendMessage(RawClient):  # pylint: disable=missing-class-docstring
    async def send_message(self,  # pylint: disable=arguments-differ
                           chat_id: Union[int, str],
                           text: str,
                           del_in: int = -1,
                           log: Union[bool, str] = False,
                           parse_mode: Optional[enums.ParseMode] = None,
                           entities: List[MessageEntity] = None,
                           disable_web_page_preview: Optional[bool] = None,
                           disable_notification: Optional[bool] = None,
                           reply_to_message_id: Optional[int] = None,
                           schedule_date: Optional[datetime] = None,
                           protect_content: Optional[bool] = None,
                           reply_markup: Union[InlineKeyboardMarkup,
                                               ReplyKeyboardMarkup,
                                               ReplyKeyboardRemove,
                                               ForceReply] = None
                           ) -> Union['types.bound.Message', bool]:
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

            parse_mode (:obj:`enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.

            entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in message text,
                which can be specified instead of *parse_mode*.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent. Unix time.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

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
                                         entities=entities,
                                         disable_web_page_preview=disable_web_page_preview,
                                         disable_notification=disable_notification,
                                         reply_to_message_id=reply_to_message_id,
                                         schedule_date=schedule_date,
                                         protect_content=protect_content,
                                         reply_markup=reply_markup)
        module = inspect.currentframe().f_back.f_globals['__name__']
        if log:
            await self._channel.fwd_msg(msg, module if isinstance(log, bool) else log)
        del_in = del_in or config.Dynamic.MSG_DELETE_TIMEOUT
        if del_in > 0:
            await asyncio.sleep(del_in)
            setattr(msg, "_client", self)
            return bool(await msg.delete())
        return types.bound.Message.parse(self, msg, module=module)
