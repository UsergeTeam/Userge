from userge import userge, Filters
from userge.db import Database

log = userge.getLogger(__name__)

welcome_table = Database.create_table("welcome")
left_table = Database.create_table("left")

welcome_list = welcome_table.find_all({'on': True}, {'_id': 1})
left_list = left_table.find_all({'on': True}, {'_id': 1})

welcome_chats = Filters.chat([])
left_chats = Filters.chat([])

for i in welcome_list:
    welcome_chats.add(i.get('_id'))

for i in left_list:
    left_chats.add(i.get('_id'))


@userge.on_cmd("setwelcome", about="Creates a welcome message in current chat :)")
async def setwel(_, message):
    if message.chat.type in ["private", "bot", "channel"]:
        await message.edit('Are you high XO\nSet welcome in a group chat')
        return

    try:
        welcome_string = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await message.edit("wrong syntax\n`.setwelcome <welcome message>`")
    else:
        new_entry = {'_id': message.chat.id, 'data': welcome_string, 'on': True}

        if welcome_table.find_one('_id', message.chat.id):
            welcome_table.update_one({'_id': message.chat.id}, new_entry)
        else:
            welcome_table.insert_one(new_entry)

        welcome_chats.add(message.chat.id)
        await message.edit(f"Welcome message has been set for the \n`{message.chat.title}`")


@userge.on_cmd("setleft", about="Creates a left message in current chat :)")
async def setleft(_, message):
    if message.chat.type in ["private", "bot", "channel"]:
        await message.edit('Are you high XO\nSet left in a group chat')
        return

    try:
        left_string = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await message.edit("wrong syntax\n`.setleft <left message>`")
    else:
        new_entry = {'_id': message.chat.id, 'data': left_string, 'on': True}

        if left_table.find_one('_id', message.chat.id):
            left_table.update_one({'_id': message.chat.id}, new_entry)
        else:
            left_table.insert_one(new_entry)

        left_chats.add(message.chat.id)
        await message.edit(f"Left message has been set for the \n`{message.chat.title}`")


@userge.on_cmd("nowelcome", about="Disables welcome message in the current chat :)")
async def nowel(_, message):
    try:
        welcome_chats.remove(message.chat.id)
    except KeyError as e:
        await message.edit(e)
    else:
        welcome_table.update_one({'_id': message.chat.id}, {'on': False})
        await message.edit("Disabled Successfully !")


@userge.on_cmd("noleft", about="Disables left message in the current chat :)")
async def noleft(_, message):
    try:
        left_chats.remove(message.chat.id)
    except KeyError as e:
        await message.edit(e)
    else:
        left_table.update_one({'_id': message.chat.id}, {'on': False})
        await message.edit("Disabled Successfully !")


@userge.on_cmd("dowelcome", about="Turns on welcome message in the current chat :)")
async def dowel(_, message):
    if welcome_table.find_one('_id', message.chat.id):
        welcome_chats.add(message.chat.id)
        welcome_table.update_one({'_id': message.chat.id}, {'on': True})
        await message.edit('I will welcome new members XD')

    else:
        await message.edit('Please set the welcome message with `.setwelcome`')


@userge.on_cmd("doleft", about="Turns on left message in the current chat :)")
async def doleft(_, message):
    if left_table.find_one('_id', message.chat.id):
        left_chats.add(message.chat.id)
        left_table.update_one({'_id': message.chat.id}, {'on': True})
        await message.edit('I will inform left members XD')

    else:
        await message.edit('Please set the left message with `.setleft`')


async def get_template(table, message):
    message_str = table.find_one('_id', message.chat.id)['data']

    user = message.from_user
    fname = user.first_name if user.first_name else ''
    lname = user.last_name if user.last_name else ''
    fullname = fname + ' ' + lname
    username = user.username if user.username else ''

    kwargs = {
        'fname': fname,
        'lname': lname,
        'fullname': fullname,
        'uname': username,
        'chat': message.chat.title if message.chat.title else "this group",
        'mention': f'<a href="tg://user?id={user.id}">{username or fullname or "user"}</a>',
    }

    return message_str.format(**kwargs)


@userge.on_new_member(welcome_chats)
async def saywel(_, message):
    welcome_message = await get_template(welcome_table, message)
    await message.reply(welcome_message)


@userge.on_left_member(left_chats)
async def sayleft(_, message):
    left_message = await get_template(left_table, message)
    await message.reply(left_message)


@userge.on_cmd("listwelcome", about="Shows the activated chats for welcome")
async def lswel(_, message):
    liststr = ""
    welcome_list = welcome_table.find_all({'on': True}, {'_id': 1, 'data': 1})

    for j in welcome_list:
        liststr += f"**{(await userge.get_chat(j.get('_id'))).title}**\n"
        liststr += f"`{j.get('data')}`\n\n"

    await message.edit(liststr or '`NO WELCOMES STARTED`')


@userge.on_cmd("listleft", about="Shows the activated chats for left")
async def lsleft(_, message):
    liststr = ""
    left_list = left_table.find_all({'on': True}, {'_id': 1, 'data': 1})

    for j in left_list:
        liststr += f"**{(await userge.get_chat(j.get('_id'))).title}**\n"
        liststr += f"`{j.get('data')}`\n\n"

    await message.edit(liststr or '`NO LEFTS STARTED`')
