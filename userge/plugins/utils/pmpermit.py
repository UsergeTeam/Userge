# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
from typing import Dict

from userge import userge, Filters, Message, Config, get_collection
from userge.utils import SafeDict

CHANNEL = userge.getCLogger(__name__)
SAVED_SETTINGS = get_collection("CONFIGS")
ALLOWED_COLLECTION = get_collection("PM_PERMIT")

allowAllPms = True
pmCounter: Dict[int, int] = {}
allowAllFilter = Filters.create(lambda _, query: bool(allowAllPms))
noPmMessage = ("Hello {fname} this is an automated message\n"
               "Please wait untill you get approved to direct message "
               "And please dont spam untill then ")


async def _init() -> None:
    global allowAllPms, noPmMessage
    async for chat in ALLOWED_COLLECTION.find({"status": 'allowed'}):
        Config.ALLOWED_CHATS.add(chat.get("_id"))
    _pm = await SAVED_SETTINGS.find_one({'_id': 'PM GUARD STATUS'})
    if _pm:
        allowAllPms = bool(_pm.get('data'))
    _pmMsg = await SAVED_SETTINGS.find_one({'_id': 'CUSTOM NOPM MESSAGE'})
    if _pmMsg:
        noPmMessage = _pmMsg.get('data')


@userge.on_cmd("allow", about={
    'header': "allows someone to contact",
    'description': "Ones someone is allowed, "
                   "Userge will not interfere or handle such private chats",
    'usage': "{tr}allow [username | userID]\nreply {tr}allow to a message, "
             "do {tr}allow in the private chat"})
async def allow(message: Message):
    userid = await get_id(message)
    if userid:
        if userid in pmCounter:
            del pmCounter[userid]
        Config.ALLOWED_CHATS.add(userid)
        a = await ALLOWED_COLLECTION.update_one(
            {'_id': userid}, {"$set": {'status': 'allowed'}}, upsert=True)
        if a.matched_count:
            await message.edit("`Already approved to direct message`")
        else:
            # todo
            # if i have blocked him
            #    unblock him
            await message.edit("`Approved to direct message`")
    else:
        await message.edit(
            "I need to reply to a user or provide the username/id or be in a private chat")


@userge.on_cmd("nopm", about={
    'header': "Activates guarding on inbox",
    'description': "Ones someone is allowed, "
                   "Userge will not interfere or handle such private chats",
    'usage': "{tr}nopm [username | userID]\nreply {tr}nopm to a message, "
             "do {tr}nopm in the private chat"})
async def denyToPm(message: Message):
    userid = await get_id(message)
    if userid:
        if userid in Config.ALLOWED_CHATS:
            Config.ALLOWED_CHATS.remove(userid)
        a = await ALLOWED_COLLECTION.delete_one({'_id': userid})
        if a.deleted_count:
            await message.edit("`Prohibitted to direct message`")
        else:
            await message.edit("`Nothing was changed`")
    else:
        await message.edit(
            "I need to reply to a user or provide the username/id or be in a private chat")


async def get_id(message: Message):
    userid = None
    if message.chat.type in ['private', 'bot']:
        userid = message.chat.id
    if message.reply_to_message:
        userid = message.reply_to_message.from_user.id
    if message.input_str:
        user = message.input_str.lstrip('@')
        try:
            userid = (await userge.get_users(user)).id
        except Exception as e:
            await message.err(str(e))
    return userid


@userge.on_filters(Filters.private & ~Filters.me & ~Config.ALLOWED_CHATS
                   & ~Filters.outgoing & ~allowAllFilter & ~Filters.service & ~Filters.bot)
async def uninvitedPmHandler(message: Message):
    user_dict = await userge.get_user_dict(message.from_user.id)
    user_dict.update({'chat': message.chat.title if message.chat.title else "this group"})

    if message.from_user.is_verified:
        return
    if message.from_user.id in pmCounter:
        if pmCounter[message.from_user.id] > 3:
            del pmCounter[message.from_user.id]
            await message.reply("**You were automatically blocked**")
            Config.ALLOWED_CHATS.add(message.from_user.id)
            await message.from_user.block()
            await asyncio.sleep(1)
            await CHANNEL.log(
                f"#BLOCKED\n{user_dict['mention']} has been blocked due to spamming in pm !! ")
        else:
            pmCounter[message.from_user.id] += 1
            await message.reply(
                f"You have {pmCounter[message.from_user.id]} out of 4 **Warnings**\n"
                "Please wait untill you get aprroved to pm !", del_in=5)

    else:
        pmCounter.update({message.from_user.id: 1})

        await message.reply(
            noPmMessage.format_map(SafeDict(**user_dict)) + '\n`- Protected by userge`')
        await asyncio.sleep(1)
        await CHANNEL.log(f"#NEW_MESSAGE\n{user_dict['mention']} has messaged you")


@userge.on_filters(Filters.private & ~Config.ALLOWED_CHATS & Filters.outgoing & ~allowAllFilter)
async def outgoing_auto_approve(message: Message):
    userID = message.chat.id
    if userID in pmCounter:
        del pmCounter[userID]
    Config.ALLOWED_CHATS.add(userID)
    await ALLOWED_COLLECTION.update_one(
        {'_id': userID}, {"$set": {'status': 'allowed'}}, upsert=True)
    user_dict = await userge.get_user_dict(userID)
    await CHANNEL.log(f"**#AUTO_APPROVED**\n{user_dict['mention']}")


@userge.on_cmd("pmguard", about={
    'header': "Switchs the pm permiting module on",
    'description': "This is switched off in default. "
                   "You can switch pmguard On or Off with this command. "
                   "When you turn on this next time, "
                   "the previously allowed chats will be there !"})
async def pmguard(message: Message):
    global allowAllPms, pmCounter
    if allowAllPms:
        allowAllPms = False
        await message.edit("`PM_guard activated`", del_in=0, log=True)
    else:
        allowAllPms = True
        await message.edit("`PM_guard deactivated`", del_in=0, log=True)
        pmCounter = {}
    await SAVED_SETTINGS.update_one(
        {'_id': 'PM GUARD STATUS'}, {"$set": {'data': allowAllPms}}, upsert=True)


@userge.on_cmd("setpmmsg", about={
    'header': "Sets the reply message",
    'description': "You can change the default message which userge gives on un-invited PMs",
    'options': {
        '{fname}': "add first name",
        '{lname}': "add last name",
        '{flname}': "add full name",
        '{uname}': "username",
        '{chat}': "chat name",
        '{mention}': "mention user"}})
async def set_custom_nopm_message(message: Message):
    global noPmMessage
    await message.edit('`Custom NOpm message saved`', log=True)
    if message.reply_to_message:
        string = message.reply_to_message.text

    else:
        string = message.input_str
    if string:
        noPmMessage = string
        await SAVED_SETTINGS.update_one(
            {'_id': 'CUSTOM NOPM MESSAGE'}, {"$set": {'data': string}}, upsert=True)


@userge.on_cmd("vpmmsg", about={'header': "Displays the reply message for uninvited PMs"})
async def view_current_noPM_msg(message: Message):
    await message.edit(noPmMessage)
