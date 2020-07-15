# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['SendAsFile']

import os
from typing import Union, Optional

import aiofiles

from userge import logging
from ...ext import RawClient
from ... import types

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  :::::  %s  :::::  !>>>"


class SendAsFile(RawClient):  # pylint: disable=missing-class-docstring
    async def send_as_file(self,
                           chat_id: Union[int, str],
                           text: str,
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

            filename (``str``, *optional*):
                file_name for output file.

            caption (``str``, *optional*):
                caption for output file.

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded
                to the log channel.
                If ``str``, the logger name will be updated.

            delete_message (``bool``, *optional*):
                If ``True``, the message will be deleted
                after sending the file.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

        Returns:
            On success, the sent Message is returned.
        """
        async with aiofiles.open(filename, "w+", encoding="utf8") as out_file:
            await out_file.write(text)
        _LOG.debug(_LOG_STR, f"Uploading {filename} To Telegram")
        msg = await self.send_document(chat_id=chat_id,
                                       document=filename,
                                       caption=caption,
                                       disable_notification=True,
                                       reply_to_message_id=reply_to_message_id)
        os.remove(filename)
        if log:
            if isinstance(log, str):
                self._channel.update(log)
            await self._channel.fwd_msg(msg)
        return types.bound.Message(self, msg)
