""" setup sudos """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio

from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid

from userge import userge, Message, config, get_collection
from .. import sudo

SAVED_SETTINGS = get_collection("CONFIGS")
SUDO_USERS_COLLECTION = get_collection("sudo_users")
SUDO_CMDS_COLLECTION = get_collection("sudo_cmds")


@userge.on_start
async def _init() -> None:
    s_o = await SAVED_SETTINGS.find_one({'_id': 'SUDO_ENABLED'})
    if s_o:
        sudo.Dynamic.ENABLED = s_o['data']
    async for i in SUDO_USERS_COLLECTION.find():
        sudo.USERS.add(i['_id'])
    async for i in SUDO_CMDS_COLLECTION.find():
        sudo.COMMANDS.add(i['_id'])


@userge.on_cmd("sudo", about={'header': "enable / disable sudo access"}, allow_channels=False)
async def sudo_(message: Message):
    """ enable / disable sudo access """
    if sudo.Dynamic.ENABLED:
        sudo.Dynamic.ENABLED = False
        await message.edit("`sudo disabled !`", del_in=3)
    else:
        sudo.Dynamic.ENABLED = True
        await message.edit("`sudo enabled !`", del_in=3)
    await SAVED_SETTINGS.update_one(
        {'_id': 'SUDO_ENABLED'}, {"$set": {'data': sudo.Dynamic.ENABLED}}, upsert=True)


@userge.on_cmd("addsudo", about={
    'header': "add sudo user",
    'usage': "{tr}addsudo [username | reply to msg]"}, allow_channels=False)
async def add_sudo(message: Message):
    """ add sudo user """
    user_id = message.input_str
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    if not user_id:
        await message.err(f'user: `{user_id}` not found!')
        return
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    try:
        user = await message.client.get_user_dict(user_id)
    except PeerIdInvalid as p_e:
        await message.err(p_e)
        return
    if user['id'] in sudo.USERS:
        await message.edit(f"user : `{user['id']}` already in **SUDO**!", del_in=5)
    else:
        sudo.USERS.add(user['id'])
        await asyncio.gather(
            SUDO_USERS_COLLECTION.insert_one({'_id': user['id'], 'men': user['mention']}),
            message.edit(f"user : `{user['id']}` added to **SUDO**!", del_in=5, log=__name__))


@userge.on_cmd("delsudo", about={
    'header': "delete sudo user",
    'flags': {'-all': "remove all sudo users"},
    'usage': "{tr}delsudo [user_id | reply to msg]\n{tr}delsudo -all"}, allow_channels=False)
async def del_sudo(message: Message):
    """ delete sudo user """
    if '-all' in message.flags:
        sudo.USERS.clear()
        await asyncio.gather(
            SUDO_USERS_COLLECTION.drop(),
            message.edit("**SUDO** users cleared!", del_in=5))
        return
    user_id = message.filtered_input_str
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    if not user_id:
        await message.err(f'user: `{user_id}` not found!')
        return
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    if not isinstance(user_id, int):
        await message.err('invalid type!')
        return
    if user_id not in sudo.USERS:
        await message.edit(f"user : `{user_id}` not in **SUDO**!", del_in=5)
    else:
        sudo.USERS.remove(user_id)
        await asyncio.gather(
            SUDO_USERS_COLLECTION.delete_one({'_id': user_id}),
            message.edit(f"user : `{user_id}` removed from **SUDO**!", del_in=5, log=__name__))


@userge.on_cmd("vsudo", about={'header': "view sudo users"}, allow_channels=False)
async def view_sudo(message: Message):
    """ view sudo users """
    if not sudo.USERS:
        await message.edit("**SUDO** users not found!", del_in=5)
        return
    out_str = '🚷 **SUDO USERS** 🚷\n\n'
    async for user in SUDO_USERS_COLLECTION.find():
        out_str += f" 🙋‍♂️ {user['men']} 🆔 `{user['_id']}`\n"
    await message.edit(out_str, del_in=0)


@userge.on_cmd("addscmd", about={
    'header': "add sudo command",
    'flags': {'-all': "add all commands to sudo"},
    'usage': "{tr}addscmd [command name]\n{tr}addscmd -all"}, allow_channels=False)
async def add_sudo_cmd(message: Message):
    """ add sudo cmd """
    if '-all' in message.flags:
        await SUDO_CMDS_COLLECTION.drop()
        sudo.COMMANDS.clear()
        tmp_ = []
        restricted = ('addsudo', 'addscmd', 'exec', 'eval', 'term', 'load', 'unload')
        for c_d in list(userge.manager.loaded_commands):
            t_c = c_d.lstrip(config.CMD_TRIGGER)
            if t_c in restricted:
                continue
            tmp_.append({'_id': t_c})
            sudo.COMMANDS.add(t_c)
        await asyncio.gather(
            SUDO_CMDS_COLLECTION.insert_many(tmp_),
            message.edit(f"**Added** all (`{len(tmp_)}`) commands to **SUDO** cmds!",
                         del_in=5, log=__name__))
        return
    cmd = message.input_str
    if not cmd:
        await message.err('input not found!')
        return
    cmd = cmd.lstrip(config.CMD_TRIGGER)
    if cmd in sudo.COMMANDS:
        await message.edit(f"cmd : `{cmd}` already in **SUDO**!", del_in=5)
    elif cmd not in (c_d.lstrip(config.CMD_TRIGGER)
                     for c_d in list(userge.manager.loaded_commands)):
        await message.edit(f"cmd : `{cmd}` 🤔, is that a command ?", del_in=5)
    else:
        sudo.COMMANDS.add(cmd)
        await asyncio.gather(
            SUDO_CMDS_COLLECTION.insert_one({'_id': cmd}),
            message.edit(f"cmd : `{cmd}` added to **SUDO**!", del_in=5, log=__name__))


@userge.on_cmd("delscmd", about={
    'header': "delete sudo commands",
    'flags': {'-all': "remove all sudo commands"},
    'usage': "{tr}delscmd [command name]\n{tr}delscmd -all"}, allow_channels=False)
async def del_sudo_cmd(message: Message):
    """ delete sudo cmd """
    if '-all' in message.flags:
        sudo.COMMANDS.clear()
        await asyncio.gather(
            SUDO_CMDS_COLLECTION.drop(),
            message.edit("**SUDO** cmds cleared!", del_in=5))
        return
    cmd = message.filtered_input_str
    if not cmd:
        await message.err('input not found!')
        return
    if cmd not in sudo.COMMANDS:
        await message.edit(f"cmd : `{cmd}` not in **SUDO**!", del_in=5)
    else:
        sudo.COMMANDS.remove(cmd)
        await asyncio.gather(
            SUDO_CMDS_COLLECTION.delete_one({'_id': cmd}),
            message.edit(f"cmd : `{cmd}` removed from **SUDO**!", del_in=5, log=__name__))


@userge.on_cmd("vscmd", about={'header': "view sudo cmds"}, allow_channels=False)
async def view_sudo_cmd(message: Message):
    """ view sudo cmds """
    if not sudo.COMMANDS:
        await message.edit("**SUDO** cmds not found!", del_in=5)
        return
    out_str = f"⛔ **SUDO CMDS** ⛔\n\n**trigger** : `{config.SUDO_TRIGGER}`\n\n"
    async for cmd in SUDO_CMDS_COLLECTION.find().sort('_id'):
        out_str += f"`{cmd['_id']}`  "
    await message.edit_or_send_as_file(out_str, del_in=0)
