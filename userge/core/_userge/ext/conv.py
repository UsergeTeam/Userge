# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import asyncio
from typing import Union, Dict, Optional

from pyrogram import Message as RawMessage, Filters, MessageHandler

from userge import logging
from userge.utils.exceptions import StopConversation
from .. import client as _client

LOG = logging.getLogger(__name__)
LOG_STR = "<<<!  :::::  %s  :::::  !>>>"

CONV_DICT: Dict[int, asyncio.Queue] = {}


class MsgLimitReached(Exception):
    """
    Exception to terminate conversation if message limit reached.
    """


class Conv:
    """
    Conversation class for userge.
    """

    def __init__(self,
                 client: '_client.Userge',
                 user: Union[str, int],
                 timeout: Union[int, float],
                 limit: int) -> None:

        self._client = client
        self._user = user
        self._timeout = timeout
        self._limit = limit
        self._chat_id: int
        self._count = 0

    @property
    def chat_id(self) -> int:
        """
        Returns chat_id.
        """

        return self._chat_id

    async def get_response(self, *, timeout: Union[int, float] = 0) -> RawMessage:
        """
        \nGets the next message that responds to a previous one.

        Parameters:
            timeout (``int`` | ``float``, *optional*):
                Timeout for waiting.
                If present this will override conversation timeout

        Returns:
            On success, the recieved Message is returned.
        """

        if self._count >= self._limit:
            raise MsgLimitReached

        response_ = await asyncio.wait_for(CONV_DICT[self._chat_id].get(),
                                           timeout or self._timeout)

        self._count += 1

        return response_

    async def send_message(self, text: str) -> RawMessage:
        """
        \nSend text messages to the conversation.

        Parameters:
            text (``str``):
                Text of the message to be sent.

        Returns:
            :obj:`Message`: On success, the sent text message is returned.
        """

        return await self._client.send_message(chat_id=self._chat_id, text=text)

    async def send_document(self, document: str) -> Optional[RawMessage]:
        """
        \nSend documents to the conversation.

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

    @staticmethod
    def init(client: '_client.Userge') -> None:
        """
        initialize the conversation method.
        """

        async def _on_conversation(_, msg: RawMessage) -> None:
            CONV_DICT[msg.from_user.id].put_nowait(msg)
            msg.continue_propagation()

        client.add_handler(
            MessageHandler(
                _on_conversation,
                Filters.create(lambda _, query: CONV_DICT and \
                    query.from_user and query.from_user.id in CONV_DICT)), 0)

    async def __aenter__(self) -> 'Conv':
        self._chat_id = int(self._user) if isinstance(self._user, int) else \
            (await self._client.get_users(self._user)).id

        CONV_DICT[self._chat_id] = asyncio.Queue(self._limit)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        CONV_DICT[self._chat_id].put_nowait(None)
        del CONV_DICT[self._chat_id]

        error = ''

        if isinstance(exc_val, asyncio.exceptions.TimeoutError):
            error = f"ended conversation with {self._chat_id}, timeout reached!"

        if isinstance(exc_val, MsgLimitReached):
            error = f"ended conversation with {self._chat_id}, message limit reached!"

        if error:
            LOG.error(LOG_STR, error)
            raise StopConversation(error)
