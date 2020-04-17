# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from userge import userge, Message, Config, get_collection

SAVED_SETTINGS = get_collection("CONFIGS")

__tmp_msg__ = SAVED_SETTINGS.find_one({'_id': 'MSG_DELETE_TIMEOUT'})
__tmp_wel__ = SAVED_SETTINGS.find_one({'_id': 'WELCOME_DELETE_TIMEOUT'})

if __tmp_msg__:
    Config.MSG_DELETE_TIMEOUT = __tmp_msg__['data']

if __tmp_wel__:
    Config.WELCOME_DELETE_TIMEOUT = __tmp_wel__['data']

del __tmp_msg__, __tmp_wel__


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

    SAVED_SETTINGS.update_one(
        {'_id': 'MSG_DELETE_TIMEOUT'}, {"$set": {'data': t_o}}, upsert=True)

    await message.edit(
        f"`Set auto message delete timeout as {t_o} seconds!`",
        del_in=3)


@userge.on_cmd("vdelto", about="__View auto message delete timeout__")
async def view_delete_timeout(message: Message):
    """view delete timeout"""

    await message.edit(
        f"Currently messages will be deleted after {Config.MSG_DELETE_TIMEOUT} seconds!",
        del_in=5)


@userge.on_cmd("swelto (\\d+)", about="""\
__Set auto welcome/left message delete timeout__

**Userge:**

    `.swelto [timeout in seconds]`

**Example:**

    `.swelto 15`
    `.swelto 0` : for disable deletion""")
async def set_welcome_timeout(message: Message):
    """set welcome/left timeout"""

    await message.edit("Setting auto welcome/left message delete timeout...")

    t_o = int(message.matches[0].group(1))
    Config.WELCOME_DELETE_TIMEOUT = t_o

    SAVED_SETTINGS.update_one(
        {'_id': 'WELCOME_DELETE_TIMEOUT'}, {"$set": {'data': t_o}}, upsert=True)

    await message.edit(
        f"`Set auto welcome/left message delete timeout as {t_o} seconds!`",
        del_in=3)


@userge.on_cmd("vwelto", about="__View auto welcome/left message delete timeout__")
async def view_welcome_timeout(message: Message):
    """view welcome/left timeout"""

    await message.edit(
        f"Currently welcome/left messages will be deleted after {Config.WELCOME_DELETE_TIMEOUT} seconds!",
        del_in=5)