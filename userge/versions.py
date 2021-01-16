# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from sys import version_info

from pyrogram import __version__ as __pyro_version__  # noqa

__major__ = 0
__minor__ = 3
__micro__ = 1

__python_version__ = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"
__license__ = "[GNU GPL v3.0](https://github.com/UsergeTeam/Userge/blob/master/LICENSE)"
__copyright__ = "[UsergeTeam](https://github.com/UsergeTeam)"
