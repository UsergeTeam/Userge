# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import asyncio
from typing import Dict

from pyrogram import Filters
from userge import userge, Message, get_collection

CHANNEL = userge.getCLogger(__name__)  # channel logger object
ALLOWED_COLLECTION = get_collection("PM_PERMIT")

allowed: Filters.chat = Filters.chat([])

for chat in ALLOWED_COLLECTION.find({"status": 'allowed'}):
    allowed.add(chat.get("_id"))

pmCounter: Dict[int, int] = {}

allowAllPms = True
allowAllFilter = Filters.create(lambda _, query: bool(allowAllPms))


@userge.on_cmd("allow", about="""\
__allows someone to contact__

    Ones someone is allowed, Userge will not interfere or handle such private chats

**syntax:**

    `.allow <@username>`
    `.allow <userID>`

    reply `.allow` to a message
    do `.allow` in the private chat""")
async def allow(message: Message):
    userid = await get_id(message)
    if userid:
        if message.from_user.id in pmCounter:
            del pmCounter[message.from_user.id]
        allowed.add(userid)
        a = ALLOWED_COLLECTION.update_one({'_id': userid}, {"$set": {'status': 'allowed'}}, upsert=True)
        if a.matched_count:
            await message.edit("`Already approved to direct message`")
        else:
            await message.edit("`Approved to direct message`")
    else:
        await message.edit("I need to reply to a user or provide the username/id or be in a private chat")


@userge.on_cmd("nopm", about="""\
__Activates guarding on inbox__

    Ones someone is allowed, Userge will not interfere or handle such private chats

**syntax:**

    `.nopm <@username>`
    `.nopm <userID>`

    reply `.nopm` to a message
    do `.nopm` in the private chat""")
async def denyToPm(message: Message):
    userid = await get_id(message)
    if userid:
        if userid in allowed:
            allowed.remove(userid)
        a = ALLOWED_COLLECTION.delete_one({'_id': userid})
        if a.deleted_count:
            await message.edit("`Prohibitted to direct message`")
        else:
            await message.edit("`Nothing was changed`")
    else:
        await message.edit("I need to reply to a user or provide the username/id or be in a private chat")


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
            message.err(str(e))
    return userid


@userge.on_filters(Filters.private & ~allowed & ~Filters.outgoing & ~allowAllFilter)
async def uninvitedPmHandler(message: Message):
    user_dict = await userge.get_user_dict(message.from_user.id)
    if message.from_user.id in pmCounter:
        if pmCounter[message.from_user.id] > 3:
            del pmCounter[message.from_user.id]
            await message.reply("**You were automatically blocked**")
            allowed.add(message.from_user.id)
            await message.from_user.block()
            await asyncio.sleep(1)
            await CHANNEL.log(f"#BLOCKED\n<a href='tg://user?id={message.from_user.id}'>"
                              f"{user_dict['uname'] or user_dict['flname']}</a> has been blocked due to spamming in "
                              f"pm !! ")
        else:
            pmCounter[message.from_user.id] += 1
            await message.reply(f"You have {pmCounter[message.from_user.id]} out of 4 **Warnings**\n"
                                f"Please wait untill you get aprroved to pm !", del_in=5)

    else:
        pmCounter.update({message.from_user.id: 1})
        await message.reply("Hello i am userge\nPlease wait untill you get approved to direct message")
        await asyncio.sleep(1)
        await CHANNEL.log(f"#NEW_MESSAGE\n<a href='tg://user?id={message.from_user.id}'>"
                          f"{user_dict['uname'] or user_dict['flname']}</a> has messaged you")


@userge.on_filters(Filters.private & ~allowed & Filters.outgoing)
async def outgoing_auto_approve(message: Message):
    userID = message.chat.id
    if message.from_user.id in pmCounter:
        del pmCounter[message.from_user.id]
    allowed.add(userID)
    ALLOWED_COLLECTION.update_one({'_id': userID}, {"$set": {'status': 'allowed'}}, upsert=True)
    user_dict = await userge.get_user_dict(userID)
    await CHANNEL.log(f"**#AUTO_APPROVED**\n<a href='tg://user?id={userID}'>"
                      f"{user_dict['uname'] or user_dict['flname']}</a>")


@userge.on_cmd("pmguard", about="""\
__Switchs the pm permiting module on__

    This is switched off in default.
    You can switch pmguard On or Off with this command.
    When you turn on this next time,
    the previously allowed chats will be there !""")
async def pmguard(message: Message):
    global allowAllPms, pmCounter
    if allowAllPms:
        allowAllPms = False
        await message.edit("`PM_guard activated`", del_in=0, log=True)
    else:
        allowAllPms = True
        await message.edit("`PM_guard deactivated`", del_in=0, log=True)
        pmCounter = {}
