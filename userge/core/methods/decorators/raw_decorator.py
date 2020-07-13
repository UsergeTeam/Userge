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

import asyncio
from typing import List, Union, Any, Callable, Optional

from pyrogram import MessageHandler, Message as RawMessage, Filters
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired

from userge import logging
from ...ext import RawClient
from ... import types, client as _client  # pylint: disable=unused-import

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  :::::  %s  :::::  !>>>"

_PYROFUNC = Callable[['types.bound.Message'], Any]


class RawDecorator(RawClient):
    """ userge raw decoretor """
    _PYRORETTYPE = Callable[[_PYROFUNC], _PYROFUNC]

    def __init__(self, **kwargs) -> None:
        self.manager = types.new.Manager(self)
        self._tasks: List[Callable[[Any], Any]] = []
        super().__init__(**kwargs)

    def on_filters(self, filters: Filters, group: int = 0,
                   allow_via_bot: bool = True) -> 'RawDecorator._PYRORETTYPE':
        """ abstract on filter method """

    def _build_decorator(self,
                         log: str,
                         filters: Filters,
                         flt: Union['types.raw.Command', 'types.raw.Filter'],
                         scope: Optional[List[str]] = None,
                         **kwargs: Union[str, bool]
                         ) -> 'RawDecorator._PYRORETTYPE':
        def decorator(func: _PYROFUNC) -> _PYROFUNC:
            async def template(_: '_client.Userge', r_m: RawMessage) -> None:
                if isinstance(flt, types.raw.Command) and r_m.chat and (r_m.chat.type not in scope):
                    try:
                        _sent = await r_m.reply(
                            "**ERROR** : `Sorry!, this command not supported "
                            f"in this chat type [{r_m.chat.type}] !`")
                        await asyncio.sleep(3)
                        await _sent.delete()
                    except ChatAdminRequired:
                        pass
                else:
                    await func(types.bound.Message(_, r_m, **kwargs))
            _LOG.debug(_LOG_STR, f"Loading => [ async def {func.__name__}(message) ] "
                       f"from {func.__module__} `{log}`")
            flt.update(func, MessageHandler(template, filters))
            self.manager.add_plugin(func.__module__).add(flt)
            return func
        return decorator
