# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

""" manage your gdrive """

import logging
import os

from userge.utils import secured_env

logging.getLogger('googleapiclient.discovery').setLevel(logging.WARNING)

G_DRIVE_CLIENT_ID = secured_env("G_DRIVE_CLIENT_ID")
G_DRIVE_CLIENT_SECRET = secured_env("G_DRIVE_CLIENT_SECRET")
G_DRIVE_PARENT_ID = os.environ.get("G_DRIVE_PARENT_ID")
G_DRIVE_INDEX_LINK = os.environ.get("G_DRIVE_INDEX_LINK")
G_DRIVE_IS_TD = bool(os.environ.get("G_DRIVE_IS_TD"))
