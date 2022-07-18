# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Conversation']

import time
import asyncio
import inspect
from typing import Union, Dict, Tuple, Optional

from pyrogram import filters as _filters
from pyrogram.filters import Filter
from pyrogram.types import Message as RawMessage
from pyrogram.handlers import MessageHandler
from pyrogram import enums

from userge import logging
from userge.utils.exceptions import StopConversation
from ... import client as _client  # pylint: disable=unused-import

_LOG = logging.getLogger(__name__)

_CL_TYPE = Union['_client.Userge', '_client.UsergeBot']
_CONV_DICT: Dict[Tuple[int, _CL_TYPE], Union[asyncio.Queue, Tuple[int, asyncio.Queue]]] = {}


class _MsgLimitReached(Exception):
    pass


class Conversation:
    """ Conversation class for userge """
    def __init__(self,
                 client: _CL_TYPE,
                 chat: Union[str, int],
                 user: Union[str, int],
                 timeout: Union[int, float],
                 limit: int) -> None:
        self._client = client
        self._chat = chat
        self._user = user
        self._timeout = timeout
        self._limit = limit
        self._chat_id: int
        self._user_id: int
        self._count = 0

    @property
    def chat_id(self) -> int:
        """ Returns chat_id """
        return self._chat_id

    async def get_response(self, *, timeout: Union[int, float] = 0,
                           mark_read: bool = False,
                           filters: Filter = None) -> RawMessage:
        """\nGets the next message that responds to a previous one.

        Parameters:
            timeout (``int`` | ``float``, *optional*):
                Timeout for waiting.
                If present this will override conversation timeout

            mark_read (``bool``, *optional*):
                marks response as read.

            filters (``pyrogram.filters.Filter``, *optional*):
                filter specific response.

        Returns:
            On success, the received Message is returned.
        """
        if self._count >= self._limit:
            raise _MsgLimitReached
        queue = _CONV_DICT[(self._chat_id, self._client)]
        if isinstance(queue, tuple):
            queue = queue[1]
        timeout = timeout or self._timeout
        start = time.time()
        while True:
            diff = time.time() - start
            response_ = await asyncio.wait_for(queue.get(), max(0.1, timeout - diff))
            if filters and callable(filters):
                found = filters(self._client, response_)
                if inspect.iscoroutine(found):
                    found = await found
                if not found:
                    continue
            break
        self._count += 1
        if mark_read:
            await self.mark_read(response_)
        return response_

    async def mark_read(self, message: Optional[RawMessage] = None) -> bool:
        """\nMarks message or chat as read.

        Parameters:
            message (:obj: `Message`, *optional*):
                single message.

        Returns:
            On success, True is returned.
        """
        return bool(
            await self._client.send_read_acknowledge(chat_id=self._chat_id, message=message))

    async def send_message(self,
                           text: str,
                           parse_mode: Optional[enums.ParseMode] = None) -> RawMessage:
        """\nSend text messages to the conversation.

        Parameters:
            text (``str``):
                Text of the message to be sent.
            parse_mode (:obj:`enums.ParseMode`, *optional*):
                parser to be used to parse text entities.

        Returns:
            :obj:`Message`: On success, the sent text message is returned.
        """
        return await self._client.send_message(chat_id=self._chat_id,
                                               text=text, parse_mode=parse_mode)

    async def send_document(self, document: str) -> Optional[RawMessage]:
        """\nSend documents to the conversation.

        Parameters:
            document (``str``):
                File to send.
                Pass a file_id as string to send a file that
                exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram
                to get a file from the Internet, or
                pass a file path as string to upload a new file
                that exists on your local machine.

        Returns:
            :obj:`Message` | ``None``: On success, the sent
            document message is returned, otherwise, in case the upload
            is deliberately stopped with
            :meth:`~Client.stop_transmission`, None is returned.
        """
        return await self._client.send_document(chat_id=self._chat_id, document=document)

    async def forward_message(self, message: RawMessage) -> RawMessage:
        """\nForward message to the conversation.

        Parameters:
            message (:obj: `Message`):
                single message.

        Returns:
            On success, forwarded message is returned.
        """
        return await self._client.forward_messages(chat_id=self._chat_id,
                                                   from_chat_id=message.chat.id,
                                                   message_ids=message.id)

    @staticmethod
    def init(client: _CL_TYPE) -> None:
        """ initialize the conversation method """
        async def _on_conversation(_, msg: RawMessage) -> None:
            data = _CONV_DICT[(msg.chat.id, client)]
            if isinstance(data, asyncio.Queue):
                data.put_nowait(msg)
            elif msg.from_user and msg.from_user.id == data[0]:
                data[1].put_nowait(msg)
            msg.continue_propagation()
        client.add_handler(
            MessageHandler(
                _on_conversation,
                _filters.create(
                    lambda _, __, query: _CONV_DICT and query.chat and (
                        query.chat.id, client
                    ) in _CONV_DICT, "conversation"
                )
            )
        )

    async def __aenter__(self) -> 'Conversation':
        self._chat_id = int(self._chat) if isinstance(self._chat, int) else \
            (await self._client.get_chat(self._chat)).id
        pack = (self._chat_id, self._client)
        if pack in _CONV_DICT:
            error = f"already started conversation {self._client} with {self._chat_id} !"
            _LOG.error(error)
            raise StopConversation(error)
        if self._user:
            self._user_id = int(self._user) if isinstance(self._user, int) else \
                (await self._client.get_users(self._user)).id
            _CONV_DICT[pack] = (self._user_id, asyncio.Queue(self._limit))
        else:
            _CONV_DICT[pack] = asyncio.Queue(self._limit)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pack = (self._chat_id, self._client)
        queue = _CONV_DICT[pack]
        if isinstance(queue, tuple):
            queue = queue[1]
        queue.put_nowait(None)
        del _CONV_DICT[pack]
        error = ''
        if isinstance(exc_val, asyncio.exceptions.TimeoutError):
            error = (f"ended conversation {self._client} with {self._chat_id}, "
                     "timeout reached!")
        if isinstance(exc_val, _MsgLimitReached):
            error = (f"ended conversation {self._client} with {self._chat_id}, "
                     "message limit reached!")
        if error:
            _LOG.error(error)
            raise StopConversation(error)
