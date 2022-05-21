# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

""" Rss Feed Plugin to get regular updates from Feed """

from os import environ

from userge import config

RSS_CHAT_ID = [int(x) for x in environ.get("RSS_CHAT_ID", str(config.LOG_CHANNEL_ID)).split()]
