# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from userge import userge, Filters, Message, get_collection
from userge.utils import SafeDict

WELCOME_COLLECTION = get_collection("welcome")
LEFT_COLLECTION = get_collection("left")

WELCOME_LIST = WELCOME_COLLECTION.find({'on': True}, {'_id': 1})
LEFT_LIST = LEFT_COLLECTION.find({'on': True}, {'_id': 1})

WELCOME_CHATS = Filters.chat([])
LEFT_CHATS = Filters.chat([])

for i in WELCOME_LIST:
    WELCOME_CHATS.add(i.get('_id'))

for i in LEFT_LIST:
    LEFT_CHATS.add(i.get('_id'))


@userge.on_cmd("setwelcome", about="""\
__Creates a welcome message in current chat :)__

**Available options:**

    `{fname}` : __add first name__
    `{lname}` : __add last name__
    `{flname}` : __add full name__
    `{uname}` : __username__
    `{chat}` : __chat name__
    `{mention}` : __mention user__
    
**Example:**

    `.setwelcome Hi {mention}, <b>Welcome</b> to {chat} chat`
    or reply `.setwelcome` to text message""")
async def setwel(msg: Message):
    await raw_set(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("setleft", about="""\
__Creates a left message in current chat :)__

**Available options:**

    `{fname}` : __add first name__
    `{lname}` : __add last name__
    `{flname}` : __add full name__
    `{uname}` : __username__
    `{chat}` : __chat name__
    `{mention}` : __mention user__
    
**Example:**

    `.setleft {flname}, <pre>Why you left :(</pre>`
    or reply `.setleft` to text message""")
async def setleft(msg: Message):
    await raw_set(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("nowelcome", about="\
__Disables and removes welcome message in the current chat__")
async def nowel(msg: Message):
    await raw_no(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("noleft", about="__Disables and removes left message in the current chat__")
async def noleft(msg: Message):
    await raw_no(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("dowelcome", about="__Turns on welcome message in the current chat__")
async def dowel(msg: Message):
    await raw_do(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("doleft", about="__Turns on left message in the current chat :)__")
async def doleft(msg: Message):
    await raw_do(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("delwelcome", about="__Delete welcome message in the current chat :)__")
async def delwel(msg: Message):
    await raw_del(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("delleft", about="__Delete left message in the current chat :)__")
async def delleft(msg: Message):
    await raw_del(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("lswelcome", about="__Shows the activated chats for welcome__")
async def lswel(msg: Message):
    await raw_ls(msg, 'Welcome', WELCOME_COLLECTION)


@userge.on_cmd("lsleft", about="__Shows the activated chats for left__")
async def lsleft(msg: Message):
    await raw_ls(msg, 'Left', LEFT_COLLECTION)


@userge.on_cmd("vwelcome", about="__Shows welcome message in current chat__")
async def viewwel(msg: Message):
    await raw_view(msg, 'Welcome', WELCOME_COLLECTION)


@userge.on_cmd("vleft", about="__Shows left message in current chat__")
async def viewleft(msg: Message):
    await raw_view(msg, 'Left', LEFT_COLLECTION)


@userge.on_new_member(WELCOME_CHATS)
async def saywel(msg: Message):
    await raw_say(msg, 'Welcome', WELCOME_COLLECTION)


@userge.on_left_member(LEFT_CHATS)
async def sayleft(msg: Message):
    await raw_say(msg, 'Left', LEFT_COLLECTION)


async def raw_set(message: Message, name, collection, chats):
    if message.chat.type in ["private", "bot", "channel"]:
        await message.err(text=f'Are you high XO\nSet {name} in a group chat')
        return

    if message.reply_to_message:
        string = message.reply_to_message.text

    else:
        string = message.input_str

    if not string:
        out = f"**Wrong Syntax**\n`.set{name.lower()} <{name.lower()} message>`"

    else:
        collection.update_one(
            {'_id': message.chat.id}, {"$set": {'data': string, 'on': True}}, upsert=True)
        chats.add(message.chat.id)
        out = f"{name} __message has been set for the__\n`{message.chat.title}`"

    await message.edit(text=out, del_in=3)


async def raw_no(message: Message, name, collection, chats):
    out = f"`First Set {name} Message!`"

    if collection.find_one_and_update({'_id': message.chat.id}, {"$set": {'on': False}}):
        if message.chat.id in chats:
            chats.remove(message.chat.id)

        out = f"`{name} Disabled Successfully!`"

    await message.edit(text=out, del_in=3)


async def raw_do(message: Message, name, collection, chats):
    out = f'Please set the {name} message with `.set{name.lower()}`'
    if collection.find_one_and_update({'_id': message.chat.id}, {"$set": {'on': True}}):
        chats.add(message.chat.id)
        out = f'`I will {name} new members XD`'

    await message.edit(text=out, del_in=3)


async def raw_del(message: Message, name, collection, chats):
    out = f"`First Set {name} Message!`"

    if collection.find_one_and_delete({'_id': message.chat.id}):
        if message.chat.id in chats:
            chats.remove(message.chat.id)

        out = f"`{name} Removed Successfully!`"

    await message.edit(text=out, del_in=3)


async def raw_view(message: Message, name, collection):
    liststr = ""
    found = collection.find_one(
        {'_id': message.chat.id}, {'data': 1, 'on': 1})

    if found:
        liststr += f"**{(await userge.get_chat(message.chat.id)).title}**\n"
        liststr += f"`{found['data']}`\n"
        liststr += f"**Active:** `{found['on']}`"

    await message.edit(
        text=liststr or f'`NO {name.upper()} STARTED`', del_in=15)


async def raw_ls(message: Message, name, collection):
    liststr = ""

    for c in collection.find():
        liststr += f"**{(await userge.get_chat(c['_id'])).title}**\n"
        liststr += f"`{c['data']}`\n"
        liststr += f"**Active:** `{c['on']}`\n\n"

    await message.edit(
        text=liststr or f'`NO {name.upper()}S STARTED`', del_in=15)


async def raw_say(message: Message, name, collection):
    message_str = collection.find_one({'_id': message.chat.id})['data']

    user = message.new_chat_members[0] if name == "Welcome" \
        else message.left_chat_member
    user_dict = await userge.get_user_dict(user.id)

    kwargs = {
        **user_dict,
        'chat': message.chat.title if message.chat.title else "this group",
        'mention': f"<a href='tg://user?id={user.id}'>" + \
            f"{user_dict['uname'] or user_dict['flname']}</a>",
    }

    await message.reply(
        text=message_str.format_map(SafeDict(**kwargs)), del_in=60)
