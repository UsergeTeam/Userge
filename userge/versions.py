# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UdaySriHarsha@Github, < https://github.com/UdaySriharsha>.
#
# This file is part of < https://github.com/UdaySriHarsha/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UdaySriHarsha/Userge/blob/master/LICENSE >
#
# All rights reserved.

from sys import version_info

from pyrogram import __version__ as __pyro_version__  # noqa

__major__ = 0
__minor__ = 1
__micro__ = 7

__python_version__ = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"

__license__ = ("[GNU GPL v3.0]"
               "(https://github.com/UdaySriHarsha/Userge/blob/master/LICENSE)")

__copyright__ = "[UdaySriHarsha](https://github.com/UdaySriHarsha)"
