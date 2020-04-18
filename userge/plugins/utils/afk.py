# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import asyncio
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from userge import userge, Message, Filters, Config, get_collection

CHANNEL = userge.getCLogger(__name__)
SAVED_SETTINGS = get_collection("CONFIGS")
AFK_COLLECTION = get_collection("AFK")

IS_AFK = False
REASON = "🤔"
USERS = {}

__tmp__ = SAVED_SETTINGS.find_one({'_id': 'AFK'})

if __tmp__:
    IS_AFK = __tmp__['on']
    REASON = __tmp__['data']

del __tmp__

for _user in AFK_COLLECTION.find():
    USERS[_user['_id']] = _user['count']

IS_AFK_FILTER = Filters.create(lambda _, query: bool(IS_AFK))

MSG_1 = f"**Sorry!** My boss is AFK due to __{REASON}__.\n" + \
        "Would ping him to look into the message soon 😉"
MSG_2 = "**Sorry!** But my boss is still not here.\nTry to ping him a little later. " + \
        f"I am sorry 😖.\nHe told me he was busy with ```{REASON}```"


@userge.on_cmd("afk", about="""\
__Set to AFK mode__

    Sets your status as AFK. Responds to anyone who tags/PM's
    you telling you are AFK. Switches off AFK when you type back anything.

**Usage:*

    `.afk [reason]`""")
async def active_afk(message: Message):
    global REASON, IS_AFK

    IS_AFK = True
    reason = message.input_str
    if reason:
        REASON = reason

    AFK_COLLECTION.drop()
    SAVED_SETTINGS.update_one(
        {'_id': 'AFK'}, {"$set": {'on': True, 'data': REASON}}, upsert=True)

    await CHANNEL.log(f"You went AFK! : `{REASON}`")
    await message.edit("You went AFK!", del_in=1)


@userge.on_filters(IS_AFK_FILTER & ~Filters.me & (Filters.mentioned | \
    (Filters.private & ~Filters.service & Config.ALLOWED_CHATS)))
async def handle_afk_incomming(message: Message):
    user_id = message.from_user.id

    if user_id in USERS:
        if not USERS[user_id] % 3:
            await message.reply(MSG_2)
        USERS[user_id] += 1

    else:
        await message.reply(MSG_1)
        USERS[user_id] = 1

    AFK_COLLECTION.update_one(
        {'_id': user_id}, {"$set": {'count': USERS[user_id]}}, upsert=True)


@userge.on_filters(IS_AFK_FILTER & Filters.outgoing, group=-1)
async def handle_afk_outgoing(message: Message):
    global IS_AFK

    IS_AFK = False

    AFK_COLLECTION.drop()
    SAVED_SETTINGS.update_one(
        {'_id': 'AFK'}, {"$set": {'on': False}}, upsert=True)

    await CHANNEL.log("I'm no longer AFK!")
    replied: Message = await message.reply(f"I'm no longer AFK!")

    if USERS:
        await replied.edit(
            f"`You recieved {sum(USERS.values())} messages while you were away. "
            "Check log for more details.\n"
            "This auto-generated message shall be self destructed in 3 seconds.`", del_in=3)

        out = ''
        for user in USERS:
            try:
                user_dict = await userge.get_user_dict(int(user))
                out += f"* {user_dict['mention']} sent you {USERS[user]} messages.\n"

            except PeerIdInvalid:
                out += f"* [{user}](tg://user?id={user}) sent you {USERS[user]} messages.\n"

        await CHANNEL.log(
            f"You've recieved {sum(USERS.values())} messages "
            f"from {len(USERS)} users while you were away!\n\n" + out)

        USERS.clear()

    else:
        await asyncio.sleep(3)
        await replied.delete()
