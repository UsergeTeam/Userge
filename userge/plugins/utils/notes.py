""" setup notes """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import userge, Message, get_collection, Config

NOTES_COLLECTION = get_collection("notes")
CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "notes", about={'header': "List all saved notes in current chat"},
    allow_channels=False, allow_bots=False)
async def view_notes(message: Message) -> None:
    """ list notes in current chat """
    out = ''
    async for note in NOTES_COLLECTION.find({'chat_id': message.chat.id}):
        if 'mid' not in note:
            continue
        out += " 📌 `{}` [**{}**] , {}\n".format(
            note['name'], 'L' if 'global' in note and not note['global'] else 'G',
            CHANNEL.get_link(note['mid']))
    if out:
        await message.edit("**--Notes saved in this chat:--**\n\n" + out, del_in=0)
    else:
        await message.err("There are no saved notes in this chat")


@userge.on_cmd(
    "delnote", about={
        'header': "Deletes a note by name",
        'usage': "{tr}delnote [note name]"},
    allow_channels=False, allow_bots=False)
async def remove_note(message: Message) -> None:
    """ delete note in current chat """
    notename = message.input_str
    if not notename:
        out = "`Wrong syntax`\nNo arguements"
    elif await NOTES_COLLECTION.find_one_and_delete(
            {'chat_id': message.chat.id, 'name': notename}):
        out = "`Successfully deleted note:` **{}**".format(notename)
    else:
        out = "`Couldn't find note:` **{}**".format(notename)
    await message.edit(text=out, del_in=3)


@userge.on_cmd(
    "gtlnote", about={
        'header': "global note to local note",
        'description': "only sudos and owner can access local notes",
        'usage': "{tr}gtlnote [note name]"},
    allow_channels=False, allow_bots=False)
async def mv_to_local_note(message: Message) -> None:
    """ global to local note """
    notename = message.input_str
    if not notename:
        out = "`Wrong syntax`\nNo arguements"
    elif await NOTES_COLLECTION.find_one_and_update(
            {'chat_id': message.chat.id, 'name': notename, 'global': True},
            {"$set": {'global': False}}):
        out = "`Successfully transferred to local note:` **{}**".format(notename)
    else:
        out = "`Couldn't find global note:` **{}**".format(notename)
    await message.edit(text=out, del_in=3)


@userge.on_cmd(
    "ltgnote", about={
        'header': "local note to global note",
        'description': "anyone can access global notes",
        'usage': "{tr}ltgnote [note name]"},
    allow_channels=False, allow_bots=False)
async def mv_to_global_note(message: Message) -> None:
    """ local to global note """
    notename = message.input_str
    if not notename:
        out = "`Wrong syntax`\nNo arguements"
    elif await NOTES_COLLECTION.find_one_and_update(
            {'chat_id': message.chat.id, 'name': notename, 'global': False},
            {"$set": {'global': True}}):
        out = "`Successfully transferred to global note:` **{}**".format(notename)
    else:
        out = "`Couldn't find local note:` **{}**".format(notename)
    await message.edit(text=out, del_in=3)


@userge.on_cmd(r"(?:#|get\s)(\S+)",
               about={'header': "Gets a note by name",
                      'usage': "#[notename]\nget notename"},
               group=-1,
               name="get_note",
               trigger='',
               filter_me=False,
               allow_channels=False,
               allow_bots=False,
               check_client=True)
async def get_note(message: Message) -> None:
    """ get any saved note """
    if not message.from_user:
        return
    can_access = message.from_user.is_self or message.from_user.id in Config.SUDO_USERS
    notename = message.matches[0].group(1)
    found = await NOTES_COLLECTION.find_one(
        {'chat_id': message.chat.id, 'name': notename}, {'mid': 1, 'global': 1})
    if found and (can_access or found['global']):
        if 'mid' not in found:
            return
        replied = message.reply_to_message
        if replied:
            reply_to_message_id = replied.message_id
        else:
            reply_to_message_id = message.message_id
        await CHANNEL.forward_stored(client=message.client,
                                     message_id=found['mid'],
                                     chat_id=message.chat.id,
                                     user_id=message.from_user.id,
                                     reply_to_message_id=reply_to_message_id)


@userge.on_cmd(r"addnote (\S+)(?:\s([\s\S]+))?",
               about={
                   'header': "Adds a note by name",
                   'options': {
                       '{fname}': "add first name",
                       '{lname}': "add last name",
                       '{flname}': "add full name",
                       '{uname}': "username",
                       '{chat}': "chat name",
                       '{count}': "chat members count",
                       '{mention}': "mention user"},
                   'usage': "{tr}addnote [note name] [content | reply to msg]"},
               allow_channels=False,
               allow_bots=False)
async def add_note(message: Message) -> None:
    """ add note to curent chat """
    notename = message.matches[0].group(1)
    content = message.matches[0].group(2)
    replied = message.reply_to_message
    if replied and replied.text:
        content = replied.text.html
    if content:
        content = "📝 **--{}--** 📝\n\n{}".format(notename, content)
    if not (content or (replied and replied.media)):
        await message.err(text="No Content Found!")
        return
    message_id = await CHANNEL.store(replied, content)
    result = await NOTES_COLLECTION.update_one(
        {'chat_id': message.chat.id, 'name': notename},
        {"$set": {'mid': message_id, 'global': False}}, upsert=True)
    out = "`{} note #{}`"
    if result.upserted_id:
        out = out.format('Added', notename)
    else:
        out = out.format('Updated', notename)
    await message.edit(text=out, del_in=3, log=__name__)
