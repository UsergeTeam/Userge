from userge import userge
from userge.db import Database
from pyrogram import Filters

log = userge.getLogger(__name__)
welcome_chats = Filters.chat([])
for i in Database("welcome").filter({'on': True}, {'_id': ''}):
    welcome_chats.add(i['_id'])


@userge.on_cmd("setwelcome", about="Creates a welcome message in current chat :)")
async def setwel(_, message: userge.MSG):
    welcome_db = Database("welcome")
    try:
        welcome_string = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await message.edit("wrong syntax\n`.setwelcome <welcome message>`")
    else:
        new_entry = {'_id': message.chat.id, 'data': welcome_string, 'on': True}
        welcome_chats.add(message.chat.id)
        welcome_db.addnew(new_entry)
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
    if welcome_db.findone('_id', message.chat.id).get('data', False):
        welcome_chats.add(message.chat.id)
        welcome_db.update({'_id': message.chat.id}, {'on': True}, 'set')
        await message.edit('I will welcome new members XD')
    else:
        await message.edit('Please set the welcome message with `.setwelcome`')


@userge.on_message(Filters.new_chat_members & welcome_chats)
async def saywel(_, message: userge.MSG):
    welcome_db = Database("welcome")
    welcome_message = welcome_db.findone('_id', message.chat.id)['data']
    await message.reply(welcome_message)

# TODO add a command to show chats where welcome is currently turned on
# TODO add formating (such as mention , first name , etc) to the welcome message
