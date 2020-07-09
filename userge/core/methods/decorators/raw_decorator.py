# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['RawDecorator']

import time
import asyncio
from traceback import format_exc
from typing import List, Union, Any, Callable, Optional

from pyrogram import (
    MessageHandler, Message as RawMessage, Filters,
    StopPropagation, ContinuePropagation)
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired, PeerIdInvalid

from userge import logging, Config
from ...ext import RawClient
from ... import types, client as _client  # pylint: disable=unused-import

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  :::::  %s  :::::  !>>>"

_PYROFUNC = Callable[['types.bound.Message'], Any]
_B_CMN_CHT: List[int] = []
_START_TO = time.time()
_B_ID = 0


async def _get_bot_chats(r_c: Union['_client.Userge', '_client._UsergeBot'],
                         r_m: RawMessage) -> List[int]:
    global _START_TO, _B_ID  # pylint: disable=global-statement
    if isinstance(r_c, _client.Userge):
        if round(time.time() - _START_TO) > 20:
            if not _B_ID:
                _B_ID = (await r_c.bot.get_me()).id
            try:
                chats = await r_c.get_common_chats(_B_ID)
                _B_CMN_CHT.clear()
                for chat in chats:
                    _B_CMN_CHT.append(chat.id)
            except PeerIdInvalid:
                pass
            _START_TO = time.time()
    else:
        if r_m.chat.id not in _B_CMN_CHT:
            _B_CMN_CHT.append(r_m.chat.id)
    return _B_CMN_CHT


class RawDecorator(RawClient):
    """ userge raw decoretor """
    _PYRORETTYPE = Callable[[_PYROFUNC], _PYROFUNC]

    def __init__(self, **kwargs) -> None:
        self.manager = types.new.Manager(self)
        self._tasks: List[Callable[[Any], Any]] = []
        super().__init__(**kwargs)

    def on_filters(self, filters: Filters, group: int = 0, allow_via_bot: bool = True,
                   check_client: bool = False) -> 'RawDecorator._PYRORETTYPE':
        """ abstract on filter method """

    def _build_decorator(self,
                         log: str,
                         filters: Filters,
                         flt: Union['types.raw.Command', 'types.raw.Filter'],
                         check_client: bool,
                         scope: Optional[List[str]] = None,
                         **kwargs: Union[str, bool]
                         ) -> 'RawDecorator._PYRORETTYPE':
        def decorator(func: _PYROFUNC) -> _PYROFUNC:
            async def template(r_c: Union['_client.Userge', '_client._UsergeBot'],
                               r_m: RawMessage) -> None:
                if RawClient.DUAL_MODE:
                    if check_client or (r_m.from_user and r_m.from_user.id in Config.SUDO_USERS):
                        if Config.USE_USER_FOR_CLIENT_CHECKS:
                            # pylint: disable=protected-access
                            if isinstance(r_c, _client._UsergeBot):
                                return
                        else:
                            if r_m.chat.id in await _get_bot_chats(r_c, r_m):
                                if isinstance(r_c, _client.Userge):
                                    return
                if isinstance(flt, types.raw.Command) and r_m.chat and (r_m.chat.type not in scope):
                    try:
                        _sent = await r_c.send_message(
                            r_m.chat.id,
                            "**ERROR** : `Sorry!, this command not supported "
                            f"in this chat type [{r_m.chat.type}] !`",
                            reply_to_message_id=r_m.message_id)
                        await asyncio.sleep(5)
                        await _sent.delete()
                    except ChatAdminRequired:
                        pass
                else:
                    try:
                        await func(types.bound.Message(r_c, r_m, **kwargs))
                    except (StopPropagation, ContinuePropagation):  # pylint: disable=W0706
                        raise
                    except Exception as f_e:  # pylint: disable=broad-except
                        _LOG.exception(_LOG_STR, f_e)
                        await self._channel.log("#ERROR #TRACEBACK\n\n"
                                                f"**Module** : `{func.__module__}`\n"
                                                f"**Function** : `{func.__name__}`\n"
                                                f"**Traceback** : ```{format_exc().strip()}```")
                        try:
                            _sent = await r_c.send_message(
                                r_m.chat.id,
                                f"**ERROR** : `{f_e}`\n__see logs for more info !__",
                                reply_to_message_id=r_m.message_id)
                            await asyncio.sleep(5)
                            await _sent.delete()
                        except ChatAdminRequired:
                            pass
            _LOG.debug(_LOG_STR, f"Loading => [ async def {func.__name__}(message) ] "
                       f"from {func.__module__} `{log}`")
            flt.update(func, MessageHandler(template, filters))
            self.manager.add_plugin(func.__module__).add(flt)
            return func
        return decorator
