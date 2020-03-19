from userge import userge, Filters
from userge.db import Database

WELCOME_TABLE = Database.create_table("welcome")
LEFT_TABLE = Database.create_table("left")

WELCOME_LIST = WELCOME_TABLE.find_all({'on': True}, {'_id': 1})
LEFT_LIST = LEFT_TABLE.find_all({'on': True}, {'_id': 1})

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
    `{fullname}` : __add full name__
    `{uname}` : __username__
    `{chat}` : __chat name__
    `{mention}` : __mention user__
    
**Example:**

    `.setwelcome Hi {mention}, Welcome to {chat} chat`""")
async def setwel(_, msg):
    await raw_set(msg, 'Welcome', WELCOME_TABLE, WELCOME_CHATS)


@userge.on_cmd("setleft",
    about="""__Creates a left message in current chat :)__

**Available options:**

    `{fname}` : __add first name__
    `{lname}` : __add last name__
    `{fullname}` : __add full name__
    `{uname}` : __username__
    `{chat}` : __chat name__
    `{mention}` : __mention user__
    
**Example:**

    `.setleft {fullname}, Why you left :(`""")
async def setleft(_, msg):
    await raw_set(msg, 'Left', LEFT_TABLE, LEFT_CHATS)


@userge.on_cmd("nowelcome", about="__Disables and removes welcome message in the current chat :)__")
async def nowel(_, msg):
    await raw_no(msg, 'Welcome', WELCOME_TABLE, WELCOME_CHATS)


@userge.on_cmd("noleft", about="__Disables and removes left message in the current chat :)__")
async def noleft(_, msg):
    await raw_no(msg, 'Left', LEFT_TABLE, LEFT_CHATS)


@userge.on_cmd("dowelcome", about="__Turns on welcome message in the current chat :)__")
async def dowel(_, msg):
    await raw_do(msg, 'Welcome', WELCOME_TABLE, WELCOME_CHATS)


@userge.on_cmd("doleft", about="__Turns on left message in the current chat :)__")
async def doleft(_, msg):
    await raw_do(msg, 'Left', LEFT_TABLE, LEFT_CHATS)


@userge.on_cmd("listwelcome", about="__Shows the activated chats for welcome__")
async def lswel(_, msg):
    await raw_ls(msg, 'Welcome', WELCOME_TABLE)


@userge.on_cmd("listleft", about="__Shows the activated chats for left__")
async def lsleft(_, msg):
    await raw_ls(msg, 'Left', LEFT_TABLE)


@userge.on_new_member(WELCOME_CHATS)
async def saywel(_, msg):
    await raw_say(msg, 'Welcome', WELCOME_TABLE)


@userge.on_left_member(LEFT_CHATS)
async def sayleft(_, msg):
    await raw_say(msg, 'Left', LEFT_TABLE)


async def raw_set(message, name, table, chats):
    if message.chat.type in ["private", "bot", "channel"]:
        await message.edit(f'Are you high XO\nSet {name} in a group chat')
        return

    string = message.matches[0].group(1)

    if string is None:
        await message.edit(f"wrong syntax\n`.set{name.lower()} <{name.lower()} message>`")

    else:
        new_entry = {'_id': message.chat.id, 'data': string, 'on': True}

        if table.find_one('_id', message.chat.id):
            table.update_one({'_id': message.chat.id}, new_entry)

        else:
            table.insert_one(new_entry)

        chats.add(message.chat.id)
        await message.edit(f"{name} message has been set for the \n`{message.chat.title}`")


async def raw_no(message, name, table, chats):
    try:
        chats.remove(message.chat.id)

    except KeyError:
        await message.edit(f"First Set {name} Message!")

    else:
        table.update_one({'_id': message.chat.id}, {'on': False})
        await message.edit(f"{name} Disabled Successfully !")


async def raw_do(message, name, table, chats):
    if table.find_one('_id', message.chat.id):
        chats.add(message.chat.id)
        table.update_one({'_id': message.chat.id}, {'on': True})

        await message.edit(f'I will {name} new members XD')

    else:
        await message.edit(f'Please set the {name} message with `.set{name.lower()}`')


async def raw_ls(message, name, table):
    liststr = ""
    list_ = table.find_all({'on': True}, {'_id': 1, 'data': 1})

    for j in list_:
        liststr += f"**{(await userge.get_chat(j.get('_id'))).title}**\n"
        liststr += f"`{j.get('data')}`\n\n"

    await message.edit(liststr or f'`NO {name.upper()}S STARTED`')


async def raw_say(message, name, table):
    message_str = table.find_one('_id', message.chat.id)['data']

    user = message.new_chat_members[0] if name == "Welcome" else message.left_chat_member
    fname = user.first_name or ''
    lname = user.last_name or ''
    username = user.username or ''

    if fname and lname:
        full_name = fname + ' ' + lname

    elif fname:
        full_name = fname

    elif lname:
        full_name = lname

    else:
        full_name = "user"

    kwargs = {
        'fname': fname,
        'lname': lname,
        'fullname': full_name,
        'uname': username,
        'chat': message.chat.title if message.chat.title else "this group",
        'mention': f'<a href="tg://user?id={user.id}">{username or full_name}</a>',
    }

    await message.reply(message_str.format(**kwargs))
