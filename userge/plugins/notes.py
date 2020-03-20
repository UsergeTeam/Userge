from userge import userge, get_collection
import asyncio

NOTES_COLLECTION = get_collection("notes")


@userge.on_cmd("notes", about="__List all saved notes__")
async def notes_active(_, message):
    out = "`There are no saved notes in this chat`"

    for note in NOTES_COLLECTION.find({'chat_id': message.chat.id}, {'name': 1}):
        if out == "`There are no saved notes in this chat`":
            out = "**--Notes saved in this chat:--**\n\n"
            out += " 🔹 `{}`\n".format(note['name'])
            
        else:
            out += " 🔹 `{}`\n".format(note['name'])

    await message.edit(out)


@userge.on_cmd("delnote",
    about="""__Deletes a note by name__

**Usage:**

    `.delnote [note name]`""")
async def remove_notes(_, message):
    notename = message.matches[0].group(1)

    if NOTES_COLLECTION.find_one_and_delete({'chat_id': message.chat.id, 'name': notename}):
        out = "`Successfully deleted note:` **{}**".format(notename)

    else:
        out = "`Couldn't find note:` **{}**".format(notename)

    await message.edit(out)
    await asyncio.sleep(3)
    await message.delete()


@userge.on_cmd(r"(\w[\w_]*)",
    about="""__Gets a note by name__

**Usage:**

    `#[notname]`""",
    trigger='#',
    only_me=False)
async def note(_, message):
    notename = message.matches[0].group(1)
    found = NOTES_COLLECTION.find_one({'chat_id': message.chat.id, 'name': notename}, {'content': 1})

    if found:
        out = "**--{}--**\n\n{}".format(notename, found['content'])
        try:
            await message.edit(out)

        except:
            await userge.send_message(
                chat_id=message.chat.id,
                text=out,
                reply_to_message_id=message.message_id
            )


@userge.on_cmd("addnote (\\w[\\w_]*)(?:\\s([\\s\\S]+))?",
    about="""__Adds a note by name__

**Usage:**

    `.addnote [note name] [content | reply to msg]`""")
async def add_filter(_, message):
    notename = message.matches[0].group(1)
    content = message.matches[0].group(2)

    if message.reply_to_message:
        content = message.reply_to_message.text

    if not content:
        await message.edit("`No Content Found!`")
        await asyncio.sleep(3)
        await message.delete()
        return

    out = "`{} note #{}`"

    if NOTES_COLLECTION.find_one_and_update(
        {'chat_id': message.chat.id, 'name': notename}, {"$set": {'content': content}}):

        out = out.format('Updated', notename)

    else:
        NOTES_COLLECTION.insert_one({'chat_id': message.chat.id, 'name': notename, 'content': content})
        out = out.format('Added', notename)

    await message.edit(out)
    await asyncio.sleep(3)
    await message.delete()