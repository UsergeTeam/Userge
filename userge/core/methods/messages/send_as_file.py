# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['SendAsFile']

import inspect
import io
from typing import Union, Optional

from pyrogram.parser import Parser

from userge import logging
from ... import types
from ...ext import RawClient

_LOG = logging.getLogger(__name__)


class SendAsFile(RawClient):  # pylint: disable=missing-class-docstring
    async def send_as_file(self,
                           chat_id: Union[int, str],
                           text: str,
                           as_raw: bool = False,
                           filename: str = "output.txt",
                           caption: str = '',
                           log: Union[bool, str] = False,
                           reply_to_message_id: Optional[int] = None) -> 'types.bound.Message':
        """\nYou can send large outputs as file

        Example:
                @userge.send_as_file(chat_id=12345, text="hello")

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages)
                you can simply use "me" or "self".
                For a contact that exists in your Telegram address book
                you can use his phone number (str).

            text (``str``):
                Text of the message to be sent.

            as_raw (``bool``, *optional*):
                If ``False``, the message will be escaped with current parse mode.
                default to ``False``.

            filename (``str``, *optional*):
                file_name for output file.

            caption (``str``, *optional*):
                caption for output file.

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded
                to the log channel.
                If ``str``, the logger name will be updated.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

        Returns:
            On success, the sent Message is returned.
        """
        if not as_raw:
            text = (await Parser(self).parse(text)).get("message")
        doc = io.BytesIO(text.encode())
        doc.name = filename

        msg = await self.send_document(chat_id=chat_id,
                                       document=doc,
                                       caption=caption[:1024],
                                       disable_notification=True,
                                       reply_to_message_id=reply_to_message_id)
        module = inspect.currentframe().f_back.f_globals['__name__']
        if log:
            await self._channel.fwd_msg(msg, module if isinstance(log, bool) else log)
        return types.bound.Message.parse(self, msg, module=module)
