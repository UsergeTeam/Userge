# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import os
import shutil

from userge import userge, Message, Config


@userge.on_cmd("cleardir", about={'header': "Clear the current working directory"})
async def clear_dir(message: Message):
    if not os.path.isdir(Config.DOWN_PATH):
        await message.edit(
            f'`working path : {Config.DOWN_PATH} not found and just created!`', del_in=5)

    else:
        shutil.rmtree(Config.DOWN_PATH, True)
        await message.edit(
            f'`working path : {Config.DOWN_PATH} cleared!`', del_in=5)

    os.mkdir(Config.DOWN_PATH)
