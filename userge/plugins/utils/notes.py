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


@userge.on_cmd("notes", about={
    'header': "List all saved notes in current chat"}, allow_channels=False)
async def view_notes(message: Message) -> None:
    """ list notes in current chat """
    out = ''
    async for note in NOTES_COLLECTION.find(
            {'chat_id': message.chat.id}, {'name': 1, 'global': 1}):
        out += " 📌 `{}` [**{}**]\n".format(
            note['name'], 'L' if 'global' in note and not note['global'] else 'G')
    if out:
        await message.edit("**--Notes saved in this chat:--**\n\n" + out, del_in=0)
    else:
        await message.err("There are no saved notes in this chat")


@userge.on_cmd("delnote", about={
    'header': "Deletes a note by name",
    'usage': "{tr}delnote [note name]"}, allow_channels=False)
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


@userge.on_cmd("gtlnote", about={
    'header': "global note to local note",
    'description': "only sudos and owner can access local notes",
    'usage': "{tr}gtlnote [note name]"}, allow_channels=False)
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


@userge.on_cmd("ltgnote", about={
    'header': "local note to global note",
    'description': "anyone can access global notes",
    'usage': "{tr}ltgnote [note name]"}, allow_channels=False)
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


@userge.on_cmd(r"(?:#|get\s)(\w[\w_]*)",
               about={'header': "Gets a note by name",
                      'usage': "#[notename]\nget notename"},
               group=-1,
               name="get_note",
               trigger='',
               filter_me=False,
               allow_channels=False)
async def get_note(message: Message) -> None:
    """ get any saved note """
    can_access = message.from_user and (
        message.from_user.is_self or message.from_user.id in Config.SUDO_USERS)
    notename = message.matches[0].group(1)
    found = await NOTES_COLLECTION.find_one(
        {'chat_id': message.chat.id, 'name': notename}, {'content': 1, 'global': 1})
    if found and (can_access or found['global']):
        out = "**--{}--**\n\n{}".format(notename, found['content'])
        await message.force_edit(text=out)


@userge.on_cmd(r"addnote (\w[\w_]*)(?:\s([\s\S]+))?",
               about={
                   'header': "Adds a note by name",
                   'usage': "{tr}addnote [note name] [content | reply to msg]"},
               allow_channels=False)
async def add_note(message: Message) -> None:
    """ add note to curent chat """
    notename = message.matches[0].group(1)
    content = message.matches[0].group(2)
    if message.reply_to_message:
        content = message.reply_to_message.text
    if not content:
        await message.err(text="No Content Found!")
        return
    out = "`{} note #{}`"
    result = await NOTES_COLLECTION.update_one(
        {'chat_id': message.chat.id, 'name': notename},
        {"$set": {'content': content, 'global': False}}, upsert=True)
    if result.upserted_id:
        out = out.format('Added', notename)
    else:
        out = out.format('Updated', notename)
    await message.edit(text=out, del_in=3, log=True)
