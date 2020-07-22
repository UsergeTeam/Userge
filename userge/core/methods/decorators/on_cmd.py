# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['OnCmd']

import re
from typing import Dict, List, Union

from pyrogram import Filters

from userge import Config
from ... import types
from . import RawDecorator


class OnCmd(RawDecorator):  # pylint: disable=missing-class-docstring
    def on_cmd(self,
               command: str,
               about: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]],
               group: int = 0,
               name: str = '',
               trigger: str = Config.CMD_TRIGGER,
               filter_me: bool = True,
               only_admins: bool = False,
               allow_private: bool = True,
               allow_bots: bool = True,
               allow_groups: bool = True,
               allow_channels: bool = True,
               allow_via_bot: bool = True,
               check_client: bool = False,
               **kwargs: Union[str, bool]
               ) -> RawDecorator._PYRORETTYPE:
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

            only_admins (``bool``, *optional*):
                If ``True``, client should be an admin,  defaults to False.

            allow_private (``bool``, *optional*):
                If ``False``, prohibit private chats,  defaults to True.

            allow_bots (``bool``, *optional*):
                If ``False``, prohibit bot chats,  defaults to True.

            allow_groups (``bool``, *optional*):
                If ``False``, prohibit group chats,  defaults to True.

            allow_channels (``bool``, *optional*):
                If ``False``, prohibit channel chats,  defaults to True.

            allow_via_bot (``bool``, *optional*):
                If ``True``, allow this via your bot,  defaults to True.

            check_client (``bool``, *optional*):
                If ``True``, check client is bot or not before execute,  defaults to False.

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
        cmd = types.raw.Command(self, cname, about, group, allow_via_bot)
        scope: List[str] = []
        if only_admins:
            scope.append('admin')
        if allow_private:
            scope.append('private')
        if allow_bots:
            scope.append('bot')
        if allow_groups:
            scope += ['group', 'supergroup']
        if allow_channels:
            scope.append('channel')
        filters_ = Filters.create(lambda _, __: cmd.is_enabled) & Filters.regex(pattern=pattern)
        if filter_me:
            outgoing_flt = Filters.create(
                lambda _, m:
                not (m.from_user and m.from_user.is_bot)
                and (m.outgoing or (m.from_user and m.from_user.is_self))
                and not (m.chat and m.chat.type == "channel" and m.edit_date)
                and (m.text.startswith(trigger) if trigger else True))
            incoming_flt = Filters.create(
                lambda _, m:
                not m.outgoing
                and (
                    (Config.OWNER_ID
                     and (m.from_user and m.from_user.id == Config.OWNER_ID))
                    or ((cname.lstrip(trigger) in Config.ALLOWED_COMMANDS)
                        and (m.from_user and m.from_user.id in Config.SUDO_USERS)))
                and (m.text.startswith(Config.SUDO_TRIGGER) if trigger else True))
            filters_ = filters_ & (outgoing_flt | incoming_flt)
        return self._build_decorator(log=f"On {pattern}", filters=filters_, flt=cmd,
                                     check_client=check_client and allow_via_bot,
                                     scope=scope, **kwargs)
