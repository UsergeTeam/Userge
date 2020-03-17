from userge import userge
from userge.db import Database
from pyrogram import Filters

log = userge.getLogger(__name__)
welcome_chats = Filters.chat([])
welcome__list = Database("welcome").filter({'on': True}, {'_id': 1})
for i in welcome__list:
    welcome_chats.add(i.get('_id'))


@userge.on_cmd("setwelcome", about="Creates a welcome message in current chat :)")
async def setwel(_, message: userge.MSG):
    welcome_db = Database("welcome")
    if message.chat.type in ["private", "bot", "channel"]:
        await message.edit('Are you high XO\nSet welcome in a group chat')
        return
    try:
        welcome_string = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await message.edit("wrong syntax\n`.setwelcome <welcome message>`")
    else:
        new_entry = {'_id': message.chat.id, 'data': welcome_string, 'on': True}
        if welcome_db.findone('_id', message.chat.id):
            welcome_db.update({'_id': message.chat.id}, new_entry, 'set')
        else:
            welcome_db.addnew(new_entry)
        welcome_chats.add(message.chat.id)
        await message.edit(f"Welcome message has been set for the \n`{message.chat.title}`")


@userge.on_cmd("nowelcome", about="Dissables welcome message in the current chat :)")
async def nowel(_, message: userge.MSG):
    try:
        welcome_chats.remove(message.chat.id)
    except KeyError as e:
        await message.edit(e)
    else:
        welcome_db = Database("welcome")
        welcome_db.update({'_id': message.chat.id}, {'on': False}, 'set')
        await message.edit("Dissabled Successfully !")


@userge.on_cmd("dowelcome", about="Turns on welcome message in the current chat :)")
async def dowel(_, message: userge.MSG):
    welcome_db = Database("welcome")
    if welcome_db.findone('_id', message.chat.id):
        welcome_chats.add(message.chat.id)
        welcome_db.update({'_id': message.chat.id}, {'on': True}, 'set')
        await message.edit('I will welcome new members XD')
    else:
        await message.edit('Please set the welcome message with `.setwelcome`')


@userge.on_message(Filters.new_chat_members & welcome_chats)
async def saywel(_, message: userge.MSG):
    welcome_db = Database("welcome")
    welcome_message = welcome_db.findone('_id', message.chat.id)['data']

    user = message.from_user
    fname = user.first_name
    lname = user.last_name
    uname = user.username
    chat = message.chat.title

    mention = f'<a href="tg://user?id={user.id}">{uname or fname}</a>'
    await message.reply(welcome_message.format(chat=chat, fname=fname, lname=lname, uname=uname, mention=mention))


@userge.on_cmd("listwelcome", about="Shows the activated chats for welcome")
async def lswel(_, message: userge.MSG):
    liststr = ''
    welcome_list = Database("welcome").filter({'on': True}, {'_id': 1, 'data': 1})
    for j in welcome_list:
        chatid = j.get('_id')
        chatname = (await userge.get_chat(chatid)).title
        welcome_msg = j.get("data")
        print(chatname, welcome_msg)
        # liststr.join(f'>--{chatname}--\n')
    # liststr = liststr if liststr != '' else '`NO WELCOMES STARTED`'
    # await message.edit(liststr)
