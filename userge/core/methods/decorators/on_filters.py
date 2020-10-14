# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['OnFilters']

from pyrogram.filters import Filter as RawFilter

from ... import types
from . import RawDecorator


class OnFilters(RawDecorator):  # pylint: disable=missing-class-docstring
    def on_filters(self,  # pylint: disable=arguments-differ
                   filters: RawFilter,
                   group: int = 0,
                   allow_private: bool = True,
                   allow_bots: bool = True,
                   allow_groups: bool = True,
                   allow_channels: bool = True,
                   only_admins: bool = False,
                   allow_via_bot: bool = True,
                   check_client: bool = True,
                   check_downpath: bool = False,
                   check_change_info_perm: bool = False,
                   check_edit_perm: bool = False,
                   check_delete_perm: bool = False,
                   check_restrict_perm: bool = False,
                   check_promote_perm: bool = False,
                   check_invite_perm: bool = False,
                   check_pin_perm: bool = False) -> RawDecorator._PYRORETTYPE:
        """\nDecorator for handling filters

        Parameters:
            filters (:obj:`~pyrogram.filters`):
                Pass one or more filters to allow only a subset of
                messages to be passed in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.

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
                If ``True``, check client is bot or not before execute, defaults to True.

            check_downpath (``bool``, *optional*):
                If ``True``, check downpath and make if not exist, defaults to False.

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
        """
        return self._build_decorator(
            types.raw.Filter.parse(client=self,
                                   filters=filters,
                                   group=group,
                                   allow_private=allow_private,
                                   allow_bots=allow_bots,
                                   allow_groups=allow_groups,
                                   allow_channels=allow_channels,
                                   only_admins=only_admins,
                                   allow_via_bot=allow_via_bot,
                                   check_client=check_client,
                                   check_downpath=check_downpath,
                                   check_change_info_perm=check_change_info_perm,
                                   check_edit_perm=check_edit_perm,
                                   check_delete_perm=check_delete_perm,
                                   check_restrict_perm=check_restrict_perm,
                                   check_promote_perm=check_promote_perm,
                                   check_invite_perm=check_invite_perm,
                                   check_pin_perm=check_pin_perm))
