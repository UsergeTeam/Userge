# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Utils']

from .get_logger import GetLogger
from .get_channel_logger import GetCLogger
from .restart import Restart
from .terminate import Terminate


class Utils(GetLogger, GetCLogger, Restart, Terminate):
    """ methods.utils """
