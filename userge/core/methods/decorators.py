# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Decorators']

import re
import asyncio
from typing import Dict, List, Union, Any, Callable, Optional

from pyrogram import Message as RawMessage, Filters, MessageHandler
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired

from userge import logging, Config
from .message import Message
from .. import client as _client
from ..ext.manager import Manager
from ..types import Command, Filtr

_PYROFUNC = Callable[[Message], Any]

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  :::::  %s  :::::  !>>>"


class Decorators:
    """ decoretors for userge """
    def __init__(self, **kwargs) -> None:
        self.manager = Manager()
        self._tasks: List[Callable[[Any], Any]] = []
        super().__init__(**kwargs)

    def add_task(self, func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """ add tasks """
        self._tasks.append(func)
        return func

    def on_cmd(self,
               command: str,
               about: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]],
               group: int = 0,
               name: str = '',
               trigger: str = Config.CMD_TRIGGER,
               filter_me: bool = True,
               allow_private: bool = True,
               allow_bots: bool = True,
               allow_groups: bool = True,
               allow_channels: bool = True,
               **kwargs: Union[str, bool]
               ) -> Callable[[_PYROFUNC], _PYROFUNC]:
        """\nDecorator for handling messages.

        Example:
                @userge.on_cmd('test', about='for testing')

        Parameters:
            command (``str``):
                command or name to execute (without trigger!).

            about (``str`` | ``dict``):
                help string or dict for command.
                {
                    'header': ``str``,
                    'description': ``str``,
                    'flags': ``str`` | ``dict``,
                    'options': ``str`` | ``dict``,
                    'types': ``str`` | ``list``,
                    'usage': ``str``,
                    'examples': ``str`` | ``list``,
                    'others': ``str``,
                    'any_title': ``str`` | ``list`` | ``dict``
                }

            group (``int``, *optional*):
                The group identifier, defaults to 0.

            name (``str``, *optional*):
                name for command.

            trigger (``str``, *optional*):
                trigger to start command.

            filter_me (``bool``, *optional*):
                If ``False``, anyone can access,  defaults to True.

            allow_private (``bool``, *optional*):
                If ``False``, prohibit private chats,  defaults to True.

            allow_bots (``bool``, *optional*):
                If ``False``, prohibit bot chats,  defaults to True.

            allow_groups (``bool``, *optional*):
                If ``False``, prohibit group chats,  defaults to True.

            allow_channels (``bool``, *optional*):
                If ``False``, prohibit channel chats,  defaults to True.

            kwargs:
                prefix (``str``, *optional*):
                    set prefix for flags, defaults to '-'.

                del_pre (``bool``, *optional*):
                    If ``True``, flags returns without prefix,
                    defaults to False.
        """
        pattern = f"^(?:\\{trigger}|\\{Config.SUDO_TRIGGER}){command.lstrip('^')}" if trigger \
            else f"^{command.lstrip('^')}"
        if [i for i in '^()[]+*.\\|?:$' if i in command]:
            match = re.match("(\\w[\\w_]*)", command)
            cname = match.groups()[0] if match else ''
            cname = name or cname
            cname = trigger + cname if cname else ''
        else:
            cname = trigger + command
            cname = name or cname
            pattern += r"(?:\s([\S\s]+))?$"
        cmd = Command(self, cname, about, group)
        scope: List[str] = []
        if allow_private:
            scope.append('private')
        if allow_bots:
            scope.append('bot')
        if allow_groups:
            scope += ['group', 'supergroup']
        if allow_channels:
            scope.append('channel')
        filters_ = Filters.regex(pattern=pattern) & Filters.create(lambda _, __: cmd.is_enabled)
        if filter_me:
            outgoing_flt = Filters.create(
                lambda _, m:
                (m.outgoing or (m.from_user and m.from_user.is_self))
                and not (m.chat and m.chat.type == "channel" and m.edit_date)
                and (m.text.startswith(trigger) if trigger else True))
            incoming_flt = Filters.create(
                lambda _, m:
                (cname.lstrip(trigger) in Config.ALLOWED_COMMANDS)
                and not m.outgoing
                and (m.from_user and m.from_user.id in Config.SUDO_USERS)
                and (m.text.startswith(Config.SUDO_TRIGGER) if trigger else True))
            filters_ = filters_ & (outgoing_flt | incoming_flt)
        return self._build_decorator(log=f"On {pattern}", filters=filters_,
                                     flt=cmd, scope=scope, **kwargs)

    def on_filters(self,
                   filters: Filters,
                   group: int = 0) -> Callable[[_PYROFUNC], _PYROFUNC]:
        """ Decorator for handling filters """
        flt = Filtr(self, group)
        filters = filters & Filters.create(lambda _, __: flt.is_enabled)
        return self._build_decorator(log=f"On Filters {filters}",
                                     filters=filters, flt=flt)

    def on_new_member(self,
                      welcome_chats: Filters.chat,
                      group: int = -2) -> Callable[[_PYROFUNC], _PYROFUNC]:
        """ Decorator for handling new members """
        flt = Filtr(self, group)
        welcome_chats = welcome_chats & Filters.create(lambda _, __: flt.is_enabled)
        return self._build_decorator(log=f"On New Member in {welcome_chats}",
                                     filters=(
                                         Filters.group & Filters.new_chat_members
                                         & welcome_chats),
                                     flt=flt)

    def on_left_member(self,
                       leaving_chats: Filters.chat,
                       group: int = -2) -> Callable[[_PYROFUNC], _PYROFUNC]:
        """ Decorator for handling left members """
        flt = Filtr(self, group)
        leaving_chats = leaving_chats & Filters.create(lambda _, __: flt.is_enabled)
        return self._build_decorator(log=f"On Left Member in {leaving_chats}",
                                     filters=(
                                         Filters.group & Filters.left_chat_member
                                         & leaving_chats),
                                     flt=flt)

    def _build_decorator(self,
                         log: str,
                         filters: Filters,
                         flt: Union[Command, Filtr],
                         scope: Optional[List[str]] = None,
                         **kwargs: Union[str, bool]
                         ) -> Callable[[_PYROFUNC], _PYROFUNC]:
        def decorator(func: _PYROFUNC) -> _PYROFUNC:
            async def template(_: '_client.Userge', r_m: RawMessage) -> None:
                if isinstance(flt, Command) and r_m.chat and (r_m.chat.type not in scope):
                    try:
                        _sent = await r_m.reply(
                            "**ERROR** : `Sorry!, this command not supported "
                            f"in this chat type [{r_m.chat.type}] !`")
                        await asyncio.sleep(3)
                        await _sent.delete()
                    except ChatAdminRequired:
                        pass
                else:
                    await func(Message(_, r_m, **kwargs))
            _LOG.debug(_LOG_STR, f"Loading => [ async def {func.__name__}(message) ] "
                       f"from {func.__module__} `{log}`")
            flt.update(func, MessageHandler(template, filters))
            self.manager.add_plugin(self, func.__module__).add(flt)
            return func
        return decorator
