# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['OnNewMember']

from pyrogram import Filters

from . import RawDecorator


class OnNewMember(RawDecorator):  # pylint: disable=missing-class-docstring
    def on_new_member(self,
                      welcome_chats: Filters.chat,
                      group: int = -2,
                      allow_via_bot: bool = True) -> RawDecorator._PYRORETTYPE:
        """\nDecorator for handling new members

        Parameters:
            welcome_chats (:obj:`~pyrogram.Filters.chat`):
                Pass Filters.chat to allow only a subset of
                messages to be passed in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.

            allow_via_bot (``bool``, *optional*):
                If ``True``, allow this via your bot,  defaults to True.
        """
        return self.on_filters(
            filters=Filters.group & Filters.new_chat_members & welcome_chats,
            group=group, allow_via_bot=allow_via_bot)
