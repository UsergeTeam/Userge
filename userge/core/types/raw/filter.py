# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Filter']

from typing import List, Dict, Callable, Any, Optional, Union

from pyrogram import enums
from pyrogram.filters import Filter as RawFilter
from pyrogram.handlers import MessageHandler
from pyrogram.handlers.handler import Handler

from userge import logging
from ... import client as _client  # pylint: disable=unused-import

_LOG = logging.getLogger(__name__)


class Filter:
    def __init__(self,
                 filters: RawFilter,
                 client: '_client.Userge',
                 group: int,
                 scope: List[enums.ChatType],
                 only_admins: bool,
                 allow_via_bot: bool,
                 check_client: bool,
                 check_downpath: bool,
                 propagate: Optional[bool],
                 check_perm: bool,
                 check_change_info_perm: bool,
                 check_edit_perm: bool,
                 check_delete_perm: bool,
                 check_restrict_perm: bool,
                 check_promote_perm: bool,
                 check_invite_perm: bool,
                 check_pin_perm: bool,
                 name: str = '') -> None:
        self.filters = filters
        self.name = name
        self.scope = scope
        self.only_admins = only_admins
        self.allow_via_bot = allow_via_bot
        self.check_client = check_client
        self.check_downpath = check_downpath
        self.propagate = propagate
        self.check_perm = check_perm
        self.check_change_info_perm = check_change_info_perm
        self.check_edit_perm = check_edit_perm
        self.check_delete_perm = check_delete_perm
        self.check_restrict_perm = check_restrict_perm
        self.check_promote_perm = check_promote_perm
        self.check_invite_perm = check_invite_perm
        self.check_pin_perm = check_pin_perm
        self.doc: Optional[str] = None
        self.plugin: Optional[str] = None
        self._loaded = False
        self._client = client
        self._group = group if group > -5 else -4
        self._func: Optional[Callable[[Any], Any]] = None
        self._handler: Optional[Handler] = None

    @classmethod
    def parse(cls, filters: RawFilter, **kwargs: Union['_client.Userge', int, bool]) -> 'Filter':
        """ parse filter """
        # pylint: disable=protected-access
        return cls(**Filter._parse(filters=filters, **kwargs))

    @staticmethod
    def _parse(allow_private: bool,
               allow_bots: bool,
               allow_groups: bool,
               allow_channels: bool,
               **kwargs: Union[RawFilter, '_client.Userge', int, bool]
               ) -> Dict[str, Union[RawFilter, '_client.Userge', int, bool]]:
        kwargs['check_client'] = kwargs['allow_via_bot'] and kwargs['check_client']

        scope = []
        if allow_bots:
            scope.append(enums.ChatType.BOT)
        if allow_private:
            scope.append(enums.ChatType.PRIVATE)
        if allow_channels:
            scope.append(enums.ChatType.CHANNEL)
        if allow_groups:
            scope += [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]
        kwargs['scope'] = scope

        kwargs['check_perm'] = kwargs['check_change_info_perm'] \
            or kwargs['check_edit_perm'] or kwargs['check_delete_perm'] \
            or kwargs['check_restrict_perm'] or kwargs['check_promote_perm'] \
            or kwargs['check_invite_perm'] or kwargs['check_pin_perm']

        return kwargs

    def __repr__(self) -> str:
        return f"<filter {self.name}>"

    @property
    def loaded(self) -> bool:
        return self._loaded

    def update(self, func: Callable[[Any], Any], template: Callable[[Any], Any]) -> None:
        """ update filter """
        self.doc = (func.__doc__ or "undefined").strip()
        self.plugin, _ = func.__module__.split('.')[-2:]

        if not self.name:
            self.name = '.'.join((self.plugin, func.__name__))

        self._func = func
        self._handler = MessageHandler(template, self.filters)

    def load(self) -> str:
        """ load the filter """
        if self._loaded or (self._client.is_bot and not self.allow_via_bot):
            return ''

        self._client.add_handler(self._handler, self._group)
        # pylint: disable=protected-access
        if self.allow_via_bot and self._client._bot is not None:
            self._client._bot.add_handler(self._handler, self._group)

        self._loaded = True
        return self.name

    def unload(self) -> str:
        """ unload the filter """
        if not self._loaded:
            return ''

        self._client.remove_handler(self._handler, self._group)
        # pylint: disable=protected-access
        if self.allow_via_bot and self._client._bot is not None:
            self._client._bot.remove_handler(self._handler, self._group)

        self._loaded = False
        return self.name
