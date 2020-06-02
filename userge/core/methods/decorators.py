# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Decorators']

import re
from typing import Dict, List, Union, Any, Callable

from pyrogram import (
    Client as RawClient, Message as RawMessage,
    Filters, MessageHandler)

from userge import logging, Config
from .message import Message
from ..ext.manager import Manager
from ..types import Command, Filtr

_PYROFUNC = Callable[[Message], Any]

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  :::::  %s  :::::  !>>>"


class Decorators:
    """decoretors for userge"""
    def __init__(self, **kwargs) -> None:
        self.manager = Manager()
        self._tasks: List[Callable[[Any], Any]] = []
        super().__init__(**kwargs)

    def add_task(self, func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """add tasks"""
        self._tasks.append(func)
        return func

    def on_cmd(self,
               command: str,
               about: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]],
               group: int = 0,
               name: str = '',
               trigger: str = Config.CMD_TRIGGER,
               filter_me: bool = True,
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

        filters_ = Filters.regex(pattern=pattern) & Filters.create(lambda _, __: cmd.is_enabled)
        filter_my_trigger = Filters.create(
            lambda _, query: query.text.startswith(trigger) if trigger else True)
        sudo_filter = Filters.create(
            lambda _, query: query.from_user
            and query.from_user.id in Config.SUDO_USERS
            and (query.text.startswith(Config.SUDO_TRIGGER) if trigger else True))
        sudo_cmd_filter = Filters.create(
            lambda _, __: cname.lstrip(trigger) in Config.ALLOWED_COMMANDS)
        if filter_me:
            filters_ = (filters_
                        & (((Filters.outgoing | Filters.me) & filter_my_trigger)
                           | (Filters.incoming & sudo_filter & sudo_cmd_filter)))
        return self._build_decorator(log=f"On {pattern}", filters=filters_,
                                     flt=cmd, **kwargs)

    def on_filters(self,
                   filters: Filters,
                   group: int = 0) -> Callable[[_PYROFUNC], _PYROFUNC]:
        """Decorator for handling filters"""
        flt = Filtr(self, group)
        filters = filters & Filters.create(lambda _, __: flt.is_enabled)
        return self._build_decorator(log=f"On Filters {filters}",
                                     filters=filters, flt=flt)

    def on_new_member(self,
                      welcome_chats: Filters.chat,
                      group: int = -2) -> Callable[[_PYROFUNC], _PYROFUNC]:
        """Decorator for handling new members"""
        flt = Filtr(self, group)
        welcome_chats = welcome_chats & Filters.create(lambda _, __: flt.is_enabled)
        return self._build_decorator(log=f"On New Member in {welcome_chats}",
                                     filters=Filters.new_chat_members & welcome_chats,
                                     flt=flt)

    def on_left_member(self,
                       leaving_chats: Filters.chat,
                       group: int = -2) -> Callable[[_PYROFUNC], _PYROFUNC]:
        """Decorator for handling left members"""
        flt = Filtr(self, group)
        leaving_chats = leaving_chats & Filters.create(lambda _, __: flt.is_enabled)
        return self._build_decorator(log=f"On Left Member in {leaving_chats}",
                                     filters=Filters.left_chat_member & leaving_chats,
                                     flt=flt)

    def _build_decorator(self,
                         log: str,
                         filters: Filters,
                         flt: Union[Command, Filtr],
                         **kwargs: Union[str, bool]
                         ) -> Callable[[_PYROFUNC], _PYROFUNC]:
        def decorator(func: _PYROFUNC) -> _PYROFUNC:
            async def template(_: RawClient, __: RawMessage) -> None:
                await func(Message(_, __, **kwargs))
            _LOG.debug(_LOG_STR, f"Loading => [ async def {func.__name__}(message) ] "
                       f"from {func.__module__} `{log}`")
            module_name = func.__module__.split('.')[-1]
            self.manager.add_plugin(self, module_name, func.__module__).add(flt)
            handler = MessageHandler(template, filters)
            if isinstance(flt, Command):
                flt.update_command(handler, func.__doc__)
            else:
                flt.update_filter(f"{module_name }.{func.__name__}", func.__doc__, handler)
            return func
        return decorator
