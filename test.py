# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os

from userge import userge


async def worker() -> None:  # pylint: disable=missing-function-docstring
    chat_id = int(os.environ.get("CHAT_ID") or 0)
    await userge.send_message(chat_id, '`build completed !`')

if __name__ == "__main__":
    userge.begin(worker())
    print('userge test has been finished!')
