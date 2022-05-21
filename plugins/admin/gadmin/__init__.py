# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

""" manage your group """

from typing import Dict, List

ENABLED_CHATS: List[int] = []
BAN_CHANNELS: List[int] = []  # list of chats which enabled ban_mode
ALLOWED: Dict[int, List[int]] = {}  # dict to store chat ids which are allowed to chat as channels
