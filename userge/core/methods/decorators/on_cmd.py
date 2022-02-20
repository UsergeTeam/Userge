# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['OnCmd']

from typing import Dict, List, Union, Optional

from userge import config
from ... import types
from . import RawDecorator


class OnCmd(RawDecorator):  # pylint: disable=missing-class-docstring
    def on_cmd(self,
               command: str,
               about: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]],
               *,
               group: int = 0,
               name: str = '',
               trigger: Optional[str] = config.CMD_TRIGGER,
               filter_me: bool = True,
               allow_private: bool = True,
               allow_bots: bool = True,
               allow_groups: bool = True,
               allow_channels: bool = True,
               only_admins: bool = False,
               allow_via_bot: bool = True,
               check_client: bool = False,
               check_downpath: bool = False,
               propagate: Optional[bool] = None,
               check_change_info_perm: bool = False,
               check_edit_perm: bool = False,
               check_delete_perm: bool = False,
               check_restrict_perm: bool = False,
               check_promote_perm: bool = False,
               check_invite_perm: bool = False,
               check_pin_perm: bool = False,
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
                If ``False``, anyone can access, defaults to True.

            allow_private (``bool``, *optional*):
                If ``False``, prohibit private chats, defaults to True.

            allow_bots (``bool``, *optional*):
                If ``False``, prohibit bot chats, defaults to True.

            allow_groups (``bool``, *optional*):
                If ``False``, prohibit group chats, defaults to True.

            allow_channels (``bool``, *optional*):
                If ``False``, prohibit channel chats, defaults to True.

            only_admins (``bool``, *optional*):
                If ``True``, client should be an admin, defaults to False.

            allow_via_bot (``bool``, *optional*):
                If ``True``, allow this via your bot, defaults to True.

            check_client (``bool``, *optional*):
                If ``True``, check client is bot or not before execute, defaults to False.

            check_downpath (``bool``, *optional*):
                If ``True``, check downpath and make if not exist, defaults to False.

            propagate (``bool``, *optional*):
                If ``False``, stop propagation to other groups,
                if ``True`` continue propagation in this group. defaults to None.

            check_change_info_perm (``bool``, *optional*):
                If ``True``, check user has change_info permission before execute,
                defaults to False.

            check_edit_perm (``bool``, *optional*):
                If ``True``, check user has edit permission before execute,
                defaults to False.

            check_delete_perm (``bool``, *optional*):
                If ``True``, check user has delete permission before execute,
                defaults to False.

            check_restrict_perm (``bool``, *optional*):
                If ``True``, check user has restrict permission before execute,
                defaults to False.

            check_promote_perm (``bool``, *optional*):
                If ``True``, check user has promote permission before execute,
                defaults to False.

            check_invite_perm (``bool``, *optional*):
                If ``True``, check user has invite permission before execute,
                defaults to False.

            check_pin_perm (``bool``, *optional*):
                If ``True``, check user has pin permission before execute,
                defaults to False.

            kwargs:
                prefix (``str``, *optional*):
                    set prefix for flags, defaults to '-'.

                del_pre (``bool``, *optional*):
                    If ``True``, flags returns without prefix,
                    defaults to False.
        """
        return self._build_decorator(
            types.raw.Command.parse(command, about,
                                    trigger or '', name, filter_me,
                                    client=self,
                                    group=group,
                                    allow_private=allow_private,
                                    allow_bots=allow_bots,
                                    allow_groups=allow_groups,
                                    allow_channels=allow_channels,
                                    only_admins=only_admins,
                                    allow_via_bot=allow_via_bot,
                                    check_client=check_client,
                                    check_downpath=check_downpath,
                                    propagate=propagate,
                                    check_change_info_perm=check_change_info_perm,
                                    check_edit_perm=check_edit_perm,
                                    check_delete_perm=check_delete_perm,
                                    check_restrict_perm=check_restrict_perm,
                                    check_promote_perm=check_promote_perm,
                                    check_invite_perm=check_invite_perm,
                                    check_pin_perm=check_pin_perm), **kwargs)
