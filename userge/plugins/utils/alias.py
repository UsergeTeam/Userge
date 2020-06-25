# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import requests

from userge import userge, Message


@userge.on_cmd("alias", about={
    'header': "Creates aliases for commands",
    'usage': "{tr}alias [[command], [command_flags]] | [alias]",
    'example': "{tr}alias paste -n | np"})
async def alias(message: Message):
    return
