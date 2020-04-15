# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from userge import userge, Message, Config


@userge.on_cmd("sdelto (\\d+)", about="""\
__Set auto message delete timeout__

**Userge:**

    `.sdelto [timeout in seconds]`

**Example:**

    `.sdelto 15`
    `.sdelto 0` : for disable deletion""")
async def set_delete_timeout(message: Message):
    """set delete timeout"""

    await message.edit("Setting auto message delete timeout...")

    t_o = int(message.matches[0].group(1))
    Config.MSG_DELETE_TIMEOUT = t_o

    await message.edit(
        f"`Set auto message delete timeout as {t_o} seconds!`",
        del_in=3)


@userge.on_cmd("vdelto", about="__View auto message delete timeout__")
async def view_delete_timeout(message: Message):
    """view delete timeout"""

    await message.edit(
        f"Currently messages will be deleted after {Config.MSG_DELETE_TIMEOUT} seconds!",
        del_in=5)