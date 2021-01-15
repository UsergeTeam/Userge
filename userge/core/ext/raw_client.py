# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['RawClient']

import asyncio
import time
from typing import Optional, Dict

import pyrogram.raw.functions as funcs
import pyrogram.raw.types as types
from pyrogram import Client
from pyrogram.session import Session
from pyrogram.raw.core import TLObject

import userge  # pylint: disable=unused-import

_LOG = userge.logging.getLogger(__name__)
_LOG_STR = "<<<!  {  (FLOOD CONTROL) sleeping %.2fs in %d  }  !>>>"


class RawClient(Client):
    """ userge raw client """
    DUAL_MODE = False
    LAST_OUTGOING_TIME = time.time()

    REQ_LOGS: Dict[int, 'ChatReq'] = {}
    DELAY_BET_MSG_REQ = 1
    MSG_REQ_PER_MIN = 20
    REQ_LOCK = asyncio.Lock()

    def __init__(self, bot: Optional['userge.core.client.UsergeBot'] = None, **kwargs) -> None:
        self._bot = bot
        super().__init__(**kwargs)
        self._channel = userge.core.types.new.ChannelLogger(self, "CORE")
        userge.core.types.new.Conversation.init(self)

    async def send(self, data: TLObject, retries: int = Session.MAX_RETRIES,
                   timeout: float = Session.WAIT_TIMEOUT, sleep_threshold: float = None):
        key = 0
        if isinstance(data, (funcs.messages.SendMessage,
                             funcs.messages.EditMessage,
                             funcs.messages.ForwardMessages)):
            if isinstance(data, funcs.messages.ForwardMessages):
                tmp = data.to_peer
            else:
                tmp = data.peer
            if isinstance(tmp, (types.InputPeerChannel, types.InputPeerChannelFromMessage)):
                key = int(tmp.channel_id)
            elif isinstance(tmp, types.InputPeerChat):
                key = int(tmp.chat_id)
            elif isinstance(tmp, (types.InputPeerUser, types.InputPeerUserFromMessage)):
                key = int(tmp.user_id)
        elif isinstance(data, funcs.channels.DeleteMessages):
            if isinstance(data.channel, (types.InputChannel, types.InputChannelFromMessage)):
                key = int(data.channel.channel_id)
        if key:
            async def slp(to_sl: float) -> None:
                if to_sl > 0.1:
                    if to_sl > 1:
                        _LOG.info(_LOG_STR, to_sl, key)
                    else:
                        _LOG.debug(_LOG_STR, to_sl, key)
                    await asyncio.sleep(to_sl)
            async with self.REQ_LOCK:
                if key in self.REQ_LOGS:
                    chat_req = self.REQ_LOGS[key]
                else:
                    chat_req = self.REQ_LOGS[key] = ChatReq()
            diff = chat_req.small_diff
            if 0 < diff < self.DELAY_BET_MSG_REQ:
                await slp(1 - diff)
            diff = chat_req.big_diff
            if diff >= 60:
                chat_req.reset()
            elif chat_req.count > self.MSG_REQ_PER_MIN:
                await slp(60 - diff)
                chat_req.reset()
            else:
                chat_req.update()
        return await super().send(data, retries, timeout, sleep_threshold)


class ChatReq:
    def __init__(self) -> None:
        self._first = self._last = time.time()
        self._count = 0

    @property
    def small_diff(self) -> float:
        return time.time() - self._last

    @property
    def big_diff(self) -> float:
        return time.time() - self._first

    @property
    def count(self) -> float:
        return self._count

    def reset(self) -> None:
        self._first = self._last = time.time()
        self._count = 1

    def update(self) -> None:
        self._last = time.time()
        self._count += 1
