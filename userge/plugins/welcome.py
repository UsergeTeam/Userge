from userge import userge, Filters, get_collection
import asyncio

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


@userge.on_cmd("setwelcome",
               about="""__Creates a welcome message in current chat :)__

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
async def setwel(_, msg):
    await raw_set(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("setleft",
               about="""__Creates a left message in current chat :)__

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
async def setleft(_, msg):
    await raw_set(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("nowelcome", about="__Disables and removes welcome message in the current chat :)__")
async def nowel(_, msg):
    await raw_no(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("noleft", about="__Disables and removes left message in the current chat :)__")
async def noleft(_, msg):
    await raw_no(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("dowelcome", about="__Turns on welcome message in the current chat :)__")
async def dowel(_, msg):
    await raw_do(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("doleft", about="__Turns on left message in the current chat :)__")
async def doleft(_, msg):
    await raw_do(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("delwelcome", about="__Delete welcome message in the current chat :)__")
async def delwel(_, msg):
    await raw_del(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("delleft", about="__Delete left message in the current chat :)__")
async def delleft(_, msg):
    await raw_del(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("lswelcome", about="__Shows the activated chats for welcome__")
async def lswel(_, msg):
    await raw_ls(msg, 'Welcome', WELCOME_COLLECTION)


@userge.on_cmd("lsleft", about="__Shows the activated chats for left__")
async def lsleft(_, msg):
    await raw_ls(msg, 'Left', LEFT_COLLECTION)


@userge.on_cmd("vwelcome", about="__Shows welcome message in current chat__")
async def viewwel(_, msg):
    await raw_view(msg, 'Welcome', WELCOME_COLLECTION)


@userge.on_cmd("vleft", about="__Shows left message in current chat__")
async def viewleft(_, msg):
    await raw_view(msg, 'Left', LEFT_COLLECTION)


@userge.on_new_member(WELCOME_CHATS)
async def saywel(_, msg):
    await raw_say(msg, 'Welcome', WELCOME_COLLECTION)


@userge.on_left_member(LEFT_CHATS)
async def sayleft(_, msg):
    await raw_say(msg, 'Left', LEFT_COLLECTION)


async def raw_set(message, name, collection, chats):
    if message.chat.type in ["private", "bot", "channel"]:
        await message.edit(f'`Are you high XO\nSet {name} in a group chat`')
        await asyncio.sleep(3)
        await message.delete()
        return

    if message.reply_to_message:
        string = message.reply_to_message.text

    else:
        string = message.matches[0].group(1)

    if string is None:
        out = f"**Wrong Syntax**\n`.set{name.lower()} <{name.lower()} message>`"

    else:
        if not collection.find_one_and_update(
            {'_id': message.chat.id}, {"$set": {'data': string}}):
            collection.insert_one({'_id': message.chat.id, 'data': string, 'on': True})

        chats.add(message.chat.id)
        out = f"{name} __message has been set for the__\n`{message.chat.title}`"

    await message.edit(out)
    await asyncio.sleep(3)
    await message.delete()


async def raw_no(message, name, collection, chats):
    out = f"`First Set {name} Message!`"

    if collection.find_one_and_update({'_id': message.chat.id}, {"$set": {'on': False}}):
        if message.chat.id in chats:
            chats.remove(message.chat.id)

        out = f"`{name} Disabled Successfully!`"

    await message.edit(out)
    await asyncio.sleep(3)
    await message.delete()


async def raw_do(message, name, collection, chats):
    out = f'Please set the {name} message with `.set{name.lower()}`'

    if collection.find_one_and_update({'_id': message.chat.id}, {"$set": {'on': True}}):
        chats.add(message.chat.id)
        out = f'`I will {name} new members XD`'
    
    await message.edit(out)
    await asyncio.sleep(3)
    await message.delete()


async def raw_del(message, name, collection, chats):
    out = f"`First Set {name} Message!`"

    if collection.find_one_and_delete({'_id': message.chat.id}):
        if message.chat.id in chats:
            chats.remove(message.chat.id)

        out = f"`{name} Removed Successfully!`"
    
    await message.edit(out)
    await asyncio.sleep(3)
    await message.delete()


async def raw_view(message, name, collection):
    liststr = ""
    found = collection.find_one({'_id': message.chat.id}, {'data': 1, 'on': 1})

    if found:
        liststr += f"**{(await userge.get_chat(message.chat.id)).title}**\n"
        liststr += f"`{found['data']}`\n"
        liststr += f"**Active:** `{found['on']}`"

    await message.edit(liststr or f'`NO {name.upper()} STARTED`')
    await asyncio.sleep(15)
    await message.delete()


async def raw_ls(message, name, collection):
    liststr = ""

    for c in collection.find():
        liststr += f"**{(await userge.get_chat(c['_id'])).title}**\n"
        liststr += f"`{c['data']}`\n"
        liststr += f"**Active:** `{c['on']}`\n\n"

    await message.edit(liststr or f'`NO {name.upper()}S STARTED`')
    await asyncio.sleep(15)
    await message.delete()


async def raw_say(message, name, collection):
    message_str = collection.find_one({'_id': message.chat.id})['data']

    user = message.new_chat_members[0] if name == "Welcome" else message.left_chat_member
    user_dict = await userge.get_user_dict(user.id)

    kwargs = {
        **user_dict,
        'chat': message.chat.title if message.chat.title else "this group",
        'mention': f"<a href='tg://user?id={user.id}'>{user_dict['uname'] or user_dict['flname']}</a>",
    }

    try:
        await message.reply(message_str.format(**kwargs))
        await asyncio.sleep(60)
        await message.delete()

    except KeyError:
        pass
