# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['RawClient']

import asyncio
from math import floor
from typing import Optional, Dict, List
from time import time, perf_counter, sleep

import pyrogram.raw.functions as funcs
import pyrogram.raw.types as types
from pyrogram import Client
from pyrogram.session import Session
from pyrogram.raw.core import TLObject

import userge  # pylint: disable=unused-import

_LOG = userge.logging.getLogger(__name__)
_LOG_STR = "FLOOD CONTROL : sleeping %.2fs in %d"


class RawClient(Client):
    """ userge raw client """
    DUAL_MODE = False
    USER_ID = 0
    BOT_ID = 0
    LAST_OUTGOING_TIME = time()
    REQ_LOGS: Dict[int, 'ChatReq'] = {}
    REQ_LOCK = asyncio.Lock()

    def __init__(self, bot: Optional['userge.core.client.UsergeBot'] = None, **kwargs) -> None:
        self._bot = bot
        super().__init__(**kwargs)
        self._channel = userge.core.types.new.ChannelLogger(self, "CORE")
        userge.core.types.new.Conversation.init(self)

    async def invoke(self, query: TLObject, retries: int = Session.MAX_RETRIES,
                     timeout: float = Session.WAIT_TIMEOUT, sleep_threshold: float = None):
        if isinstance(query, funcs.account.DeleteAccount) or query.ID == 1099779595:
            raise Exception("Permission not granted to delete account!")
        key = 0
        if isinstance(query, (funcs.messages.SendMessage,
                              funcs.messages.SendMedia,
                              funcs.messages.SendMultiMedia,
                              funcs.messages.EditMessage,
                              funcs.messages.ForwardMessages)):
            if isinstance(query, funcs.messages.ForwardMessages):
                tmp = query.to_peer
            else:
                tmp = query.peer
            if isinstance(query, funcs.messages.SendMedia) and isinstance(
                    query.media, (types.InputMediaUploadedDocument,
                                  types.InputMediaUploadedPhoto)):
                tmp = None
            if tmp:
                if isinstance(tmp, (types.InputPeerChannel, types.InputPeerChannelFromMessage)):
                    key = int(tmp.channel_id)
                elif isinstance(tmp, types.InputPeerChat):
                    key = int(tmp.chat_id)
                elif isinstance(tmp, (types.InputPeerUser, types.InputPeerUserFromMessage)):
                    key = int(tmp.user_id)
        elif isinstance(query, funcs.channels.DeleteMessages) and isinstance(
                query.channel, (types.InputChannel, types.InputChannelFromMessage)):
            key = int(query.channel.channel_id)
        if key:
            async with self.REQ_LOCK:
                try:
                    req = self.REQ_LOGS[key]
                except KeyError:
                    req = self.REQ_LOGS[key] = ChatReq()
            async with req.lock:
                now = perf_counter()
                req.update(now - 60)
                if req.has:
                    to_sl = 0.0
                    diff = now - req.last
                    if 0 < diff < 1:
                        to_sl = 1 - diff
                    diff = now - req.first
                    if req.count > 18:
                        to_sl = max(to_sl, 60 - diff)
                    if to_sl > 0:
                        if to_sl > 1:
                            _LOG.info(_LOG_STR, to_sl, key)
                        else:
                            _LOG.debug(_LOG_STR, to_sl, key)
                        await asyncio.sleep(to_sl)
                        now += to_sl
                count = 0
                counter = floor(now - 1)
                for r in self.REQ_LOGS.values():
                    if r.has and r.last > counter:
                        count += 1
                if count > 25:
                    _LOG.info(_LOG_STR, 1, key)
                    sleep(1)
                    now += 1
                req.add(now)
        return await super().invoke(query, retries, timeout, sleep_threshold)


class ChatReq:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._logs: List[float] = []

    @property
    def lock(self):
        return self._lock

    @property
    def has(self) -> bool:
        return len(self._logs) != 0

    @property
    def first(self) -> float:
        return self._logs[0]

    @property
    def last(self) -> Optional[float]:
        return self._logs[-1]

    @property
    def count(self) -> int:
        return len(self._logs)

    def add(self, log: float) -> None:
        self._logs.append(log)

    def update(self, t: float) -> None:
        self._logs = [i for i in self._logs if i > t]
