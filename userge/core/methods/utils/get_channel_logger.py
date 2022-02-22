# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['GetCLogger']

import inspect

from ... import types
from ...ext import RawClient


class GetCLogger(RawClient):  # pylint: disable=missing-class-docstring
    # pylint: disable=invalid-name
    def getCLogger(self, name: str = '') -> 'types.new.ChannelLogger':
        """ This returns new channel logger object """
        if not name:
            name = inspect.currentframe().f_back.f_globals['__name__']

        return types.new.ChannelLogger(self, name)
