# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# Author: SnapDragon7410 (t.me/null7410)
# All rights reserved.

import requests

from userge import userge, Message, get_collection


ALIAS_BASE = get_collection("ALIAS_BASE")
aliases = {}

def create_alias_func(data):
    async def wrapper(message: Message):
        func = userge._collection[data["command"]]
        message.flags = data["flags"]
        return await func(message)
    return wrapper

def create_alias(data):
    wrapper = create_alias_func(data)
    userge.on_cmd(data["alias"], about={
        'header': "Alias of " + data["command"],
        'usage': "{tr}" + data["alias"]})(wrapper)
    aliases.update({data["alias"]: wrapper})

@userge.on_cmd("alias", about={
    'header': "Creates aliases for commands",
    'usage': "{tr}alias [[command], [flags]] | [alias]",
    'example': "{tr}alias paste -n | np"})
async def alias(message: Message):
    await message.edit("Processing...")
    raw_data = message.text.split(" ", maxsplit=2)[1:]
    if len(raw_data) == 0:
        await message.err("Zero inputs.\n"
                         "Check `.help alias` for more.")
        return
    cleaned_data = [x.strip() for x in raw_data.split("|")]
    if len(cleaned_data) != 2:
        await message.err("Add your alias.\n"
                         "Check `.help alias` for more.")
        return
    command_flags = cleaned_data[0].split(" ")
    if command_flags[0].startswith("-"):
        await message.err("Invalid Syntax.\n"
                         "Check `.help alias` for more.")
        return
    elif not command_flags[0].isalpha():
        await message.err("Invalid Characters as command.\n"
                         "Check `.help alias` for more.")
        return
    if any([not x.startswith("-") for x in command_flags[1:]]):
        await message.err("Alias does not support input.\n"
                         "Check `.help alias` for more.")
        return
    if not command_flags[0] in userge._collection:
        await message.err("Command does not exist.\n"
                         "Check `.help alias` for more.")
        return
    data = dict(type="alias", alias=cleaned_data[1], command=command_flags[0], flags=[x.startswith("-") for x in command_flags[1:]])
    if ALIAS_BASE.find_one({"alias": cleaned_data[1]}):
        await message.err("Alias already exists.\n"
                         "Check `.help alias` for more.")
        return
    ALIAS_BASE.insert_one(data)
    create_alias(data)
    await message.edit(command_flags[0] + " has been successfully aliased to " + cleaned_data[1])
    return

@userge.on_cmd("remalias", about={
    'header': "Removes previously created aliases.",
    'usage': "{tr}remalias [alias]",
    'example': "{tr}remalias np"})
async def remove_alias(message: Message):
    alias = message.input_str
    if not alias:
        await message.err("Alias needed to delete.\n"
                         "Check `.help alias` for more.")
        return
    if not alias in aliases:
        await message.err("Alias does not exist.")
        return
    ALIAS_BASE.delete_one({"alias": alias})
    await message.edit(alias + " has been successfully deleted.\n"
                      "Restart for changes to take effect.")
    return

def start_alias():
    for data in ALIAS_BASE.find_many({"type": "alias"}):
        create_alias(data)

start_alias()
