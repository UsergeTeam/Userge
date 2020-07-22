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

from pyrogram import Filters

from ... import types
from . import RawDecorator


class OnFilters(RawDecorator):  # pylint: disable=missing-class-docstring
    def on_filters(self,
                   filters: Filters,
                   group: int = 0,
                   allow_via_bot: bool = True,
                   check_client: bool = True) -> RawDecorator._PYRORETTYPE:
        """\nDecorator for handling filters

        Parameters:
            filters (:obj:`~pyrogram.Filters`):
                Pass one or more filters to allow only a subset of
                messages to be passed in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.

            allow_via_bot (``bool``, *optional*):
                If ``True``, allow this via your bot,  defaults to True.

            check_client (``bool``, *optional*):
                If ``True``, check client is bot or not before execute,  defaults to True.
        """
        flt = types.raw.Filter(self, group, allow_via_bot)
        filters = Filters.create(lambda _, __: flt.is_enabled) & filters
        return self._build_decorator(log=f"On Filters {filters}", filters=filters,
                                     flt=flt, check_client=check_client and allow_via_bot)
