import functools
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


def raw_set(name, table, chats):

    def decorator(func):

        @functools.wraps(func)
        async def wrapper(_, message):

            if message.chat.type in ["private", "bot", "channel"]:
                await message.edit(f'Are you high XO\nSet {name} in a group chat')
                return

            try:
                string = message.text.split(" ", maxsplit=1)[1]

            except IndexError:
                await message.edit(f"wrong syntax\n`.set{name.lower()} <{name.lower()} message>`")

            else:
                new_entry = {'_id': message.chat.id, 'data': string, 'on': True}

                if table.find_one('_id', message.chat.id):
                    table.update_one({'_id': message.chat.id}, new_entry)

                else:
                    table.insert_one(new_entry)

                chats.add(message.chat.id)
                await message.edit(f"{name} message has been set for the \n`{message.chat.title}`")

        return wrapper

    return decorator


def raw_on(name, table, chats):

    def decorator(func):

        @functools.wraps(func)
        async def wrapper(_, message):

            try:
                chats.remove(message.chat.id)

            except KeyError:
                await message.edit(f"First Set {name} Message!")

            else:
                table.update_one({'_id': message.chat.id}, {'on': False})
                await message.edit(f"{name} Disabled Successfully !")

        return wrapper

    return decorator


def raw_do(name, table, chats):

    def decorator(func):

        @functools.wraps(func)
        async def wrapper(_, message):

            if table.find_one('_id', message.chat.id):
                chats.add(message.chat.id)
                table.update_one({'_id': message.chat.id}, {'on': True})

                await message.edit(f'I will {name} new members XD')

            else:
                await message.edit(f'Please set the {name} message with `.set{name.lower()}`')

        return wrapper

    return decorator


def raw_say(table):

    def decorator(func):

        @functools.wraps(func)
        async def wrapper(_, message):

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

            await message.reply(message_str.format(**kwargs))

        return wrapper

    return decorator


def raw_ls(name, table):

    def decorator(func):

        @functools.wraps(func)
        async def wrapper(_, message):
            
            liststr = ""
            list_ = table.find_all({'on': True}, {'_id': 1, 'data': 1})

            for j in list_:
                liststr += f"**{(await userge.get_chat(j.get('_id'))).title}**\n"
                liststr += f"`{j.get('data')}`\n\n"

            await message.edit(liststr or f'`NO {name.upper()}S STARTED`')

        return wrapper

    return decorator


@userge.on_cmd("setwelcome", about="Creates a welcome message in current chat :)")
@raw_set('Welcome', welcome_table, welcome_chats)
async def setwel(_, message):
    pass


@userge.on_cmd("setleft", about="Creates a left message in current chat :)")
@raw_set('Left', left_table, left_chats)
async def setleft(_, message):
    pass


@userge.on_cmd("nowelcome", about="Disables welcome message in the current chat :)")
@raw_on('Welcome', welcome_table, welcome_chats)
async def nowel(_, message):
    pass


@userge.on_cmd("noleft", about="Disables left message in the current chat :)")
@raw_on('Left', left_table, left_chats)
async def noleft(_, message):
    pass


@userge.on_cmd("dowelcome", about="Turns on welcome message in the current chat :)")
@raw_do('Welcome', welcome_table, welcome_chats)
async def dowel(_, message):
    pass


@userge.on_cmd("doleft", about="Turns on left message in the current chat :)")
@raw_do('Left', left_table, left_chats)
async def doleft(_, message):
    pass


@userge.on_new_member(welcome_chats)
@raw_say(welcome_table)
async def saywel(_, message):
    pass

@userge.on_left_member(left_chats)
@raw_say(left_table)
async def sayleft(_, message):
    pass


@userge.on_cmd("listwelcome", about="Shows the activated chats for welcome")
@raw_ls('Welcome', welcome_table)
async def lswel(_, message):
    pass


@userge.on_cmd("listleft", about="Shows the activated chats for left")
@raw_ls('Left', left_table)
async def lsleft(_, message):
    pass
