""" set or view your timeouts """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import userge, Message, Config, get_collection

SAVED_SETTINGS = get_collection("CONFIGS")


async def _init() -> None:
    msg_t = await SAVED_SETTINGS.find_one({'_id': 'MSG_DELETE_TIMEOUT'})
    if msg_t:
        Config.MSG_DELETE_TIMEOUT = msg_t['data']
    wel_t = await SAVED_SETTINGS.find_one({'_id': 'WELCOME_DELETE_TIMEOUT'})
    if wel_t:
        Config.WELCOME_DELETE_TIMEOUT = wel_t['data']
    pp_t = await SAVED_SETTINGS.find_one({'_id': 'AUTOPIC_TIMEOUT'})
    if pp_t:
        Config.AUTOPIC_TIMEOUT = pp_t['data']
    es_t = await SAVED_SETTINGS.find_one({'_id': 'EDIT_SLEEP_TIMEOUT'})
    if es_t:
        Config.EDIT_SLEEP_TIMEOUT = es_t['data']


@userge.on_cmd("sdelto (\\d+)", about={
    'header': "Set auto message delete timeout",
    'usage': "{tr}sdelto [timeout in seconds]",
    'examples': "{tr}sdelto 15\n{tr}sdelto 0 : for disable deletion"})
async def set_delete_timeout(message: Message):
    """ set delete timeout """
    await message.edit("`Setting auto message delete timeout...`")
    t_o = int(message.matches[0].group(1))
    Config.MSG_DELETE_TIMEOUT = t_o
    await SAVED_SETTINGS.update_one(
        {'_id': 'MSG_DELETE_TIMEOUT'}, {"$set": {'data': t_o}}, upsert=True)
    if t_o:
        await message.edit(
            f"`Set auto message delete timeout as {t_o} seconds!`", del_in=3)
    else:
        await message.edit("`Auto message deletion disabled!`", del_in=3)


@userge.on_cmd("vdelto", about={'header': "View auto message delete timeout"})
async def view_delete_timeout(message: Message):
    """ view delete timeout """
    if Config.MSG_DELETE_TIMEOUT:
        await message.edit(
            f"`Messages will be deleted after {Config.MSG_DELETE_TIMEOUT} seconds!`",
            del_in=5)
    else:
        await message.edit("`Auto message deletion disabled!`", del_in=3)


@userge.on_cmd("swelto (\\d+)", about={
    'header': "Set auto welcome/left message delete timeout",
    'usage': "{tr}swelto [timeout in seconds]",
    'examples': "{tr}swelto 15\n{tr}swelto 0 : for disable deletion"})
async def set_welcome_timeout(message: Message):
    """ set welcome/left timeout """
    await message.edit("`Setting auto welcome/left message delete timeout...`")
    t_o = int(message.matches[0].group(1))
    Config.WELCOME_DELETE_TIMEOUT = t_o
    await SAVED_SETTINGS.update_one(
        {'_id': 'WELCOME_DELETE_TIMEOUT'}, {"$set": {'data': t_o}}, upsert=True)
    if t_o:
        await message.edit(
            f"`Set auto welcome/left message delete timeout as {t_o} seconds!`", del_in=3)
    else:
        await message.edit("`Auto welcome/left message deletion disabled!`", del_in=3)


@userge.on_cmd("vwelto", about={'header': "View auto welcome/left message delete timeout"})
async def view_welcome_timeout(message: Message):
    """ view welcome/left timeout """
    if Config.WELCOME_DELETE_TIMEOUT:
        await message.edit(
            "`Welcome/Left messages will be deleted after "
            f"{Config.WELCOME_DELETE_TIMEOUT} seconds!`",
            del_in=5)
    else:
        await message.edit("`Auto welcome/left message deletion disabled!`", del_in=3)


@userge.on_cmd("sapicto (\\d+)", about={
    'header': "Set auto profile picture timeout",
    'usage': "{tr}sapicto [timeout in seconds]",
    'examples': "{tr}sapicto 60"})
async def set_app_timeout(message: Message):
    """ set auto profile picture timeout """
    t_o = int(message.matches[0].group(1))
    if t_o < 15:
        await message.err("too short! (min = 15sec)")
        return
    await message.edit("`Setting auto profile picture timeout...`")
    Config.AUTOPIC_TIMEOUT = t_o
    await SAVED_SETTINGS.update_one(
        {'_id': 'AUTOPIC_TIMEOUT'}, {"$set": {'data': t_o}}, upsert=True)
    await message.edit(
        f"`Set auto profile picture timeout as {t_o} seconds!`", del_in=3)


@userge.on_cmd("vapicto", about={'header': "View auto profile picture timeout"})
async def view_app_timeout(message: Message):
    """ view profile picture timeout """
    await message.edit(
        f"`Profile picture will be updated after {Config.AUTOPIC_TIMEOUT} seconds!`",
        del_in=5)


@userge.on_cmd("sesto (\\d+)", about={
    'header': "Set edit sleep timeout",
    'usage': "{tr}sesto [timeout in seconds]",
    'examples': "{tr}sesto 10"})
async def set_es_timeout(message: Message):
    """ set edit sleep timeout """
    t_o = int(message.matches[0].group(1))
    if t_o < 5:
        await message.err("too short! (min = 5sec)")
        return
    await message.edit("`Setting edit sleep timeout...`")
    Config.EDIT_SLEEP_TIMEOUT = t_o
    await SAVED_SETTINGS.update_one(
        {'_id': 'EDIT_SLEEP_TIMEOUT'}, {"$set": {'data': t_o}}, upsert=True)
    await message.edit(
        f"`Set edit sleep timeout as {t_o} seconds!`", del_in=3)


@userge.on_cmd("vesto", about={'header': "View edit sleep timeout"})
async def view_es_timeout(message: Message):
    """ view edit sleep timeout """
    await message.edit(
        f"`Current edit sleep timeout = {Config.EDIT_SLEEP_TIMEOUT} seconds!`",
        del_in=5)
