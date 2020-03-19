import os
import urbandict
from json import dumps
from datetime import datetime
from . import get_all_plugins
from urllib.error import HTTPError
from googletrans import Translator, LANGUAGES
from userge import userge, Config


@userge.on_cmd("ping", about="__check how long it takes to ping your userbot__")
async def pingme(_, message):
    start = datetime.now()

    await message.edit('`Pong!`')

    end = datetime.now()
    ms = (end - start).microseconds / 1000

    await message.edit(f"**Pong!**\n`{ms} ms`")


@userge.on_cmd("help", about="__to know how to use **USERGE** commands__")
async def helpme(_, message):
    cmd = message.matches[0].group(1)
    out_str = ""

    if cmd is None:
        out_str += """**--Which command you want ?--**\n\n**Usage**:\n\n\t`.help [command]`\n\n**Available Commands:**\n\n"""

        for cmd in sorted(userge.get_help()):
            out_str += f"\t`.{cmd}`\n"

    else:
        out = userge.get_help(cmd.strip('.'))
        out_str += f"`.{cmd}`\n\n{out}" if out else "__command not found!__"

    await message.edit(out_str)


@userge.on_cmd("json",
    about="""__message object to json__

**Usage:**

    reply `.json` to any message""")
async def jsonify(_, message):
    the_real_message = str(message.reply_to_message) \
        if message.reply_to_message \
            else str(message)

    if len(the_real_message) > Config.MAX_MESSAGE_LENGTH:
        await userge.send_output_as_file(
            output=the_real_message,
            message=message,
            filename="json.txt",
            caption="Too Large"
        )

    else:
        await message.edit(the_real_message)


@userge.on_cmd("all", about="__list all plugins in plugins/ path__")
async def getplugins(_, message):
    all_plugins = await get_all_plugins()

    out_str = "**--All Userge Plugins--**\n\n"

    for plugin in all_plugins:
        out_str += f"\t`{plugin}`\n"

    await message.edit(out_str)


@userge.on_cmd("del", about="__delete replied message__")
async def del_msg(_, message):
    msg_ids = [message.message_id]

    if message.reply_to_message:
        msg_ids.append(message.reply_to_message.message_id)

    await userge.delete_messages(message.chat.id, msg_ids)


@userge.on_cmd("ids",
    about="""__display ids__

**Usage:**

reply `.ids` any message, file or just send this command""")
async def getids(_, message):
    out_str = f"💁 Current Chat ID: `{message.chat.id}`"

    if message.reply_to_message:
        out_str += f"\n🙋‍♂️ From User ID: `{message.reply_to_message.from_user.id}`"
        file_id = None

        if message.reply_to_message.media:
            if message.reply_to_message.audio:
                file_id = message.reply_to_message.audio.file_id

            elif message.reply_to_message.document:
                file_id = message.reply_to_message.document.file_id

            elif message.reply_to_message.photo:
                file_id = message.reply_to_message.photo.file_id

            elif message.reply_to_message.sticker:
                file_id = message.reply_to_message.sticker.file_id

            elif message.reply_to_message.voice:
                file_id = message.reply_to_message.voice.file_id

            elif message.reply_to_message.video_note:
                file_id = message.reply_to_message.video_note.file_id

            elif message.reply_to_message.video:
                file_id = message.reply_to_message.video.file_id

            if file_id is not None:
                out_str += f"\n📄 File ID: `{file_id}`"

    await message.edit(out_str)


@userge.on_cmd("admins",
    about="""__View or mention admins in chat__

**Available Flags:**
`--m` : __mention all admins__
`--mc` : __only mention creator__
`--id` : __show ids__

**Usage:**

    `.admins [any flag] [chatid]`""")
async def mentionadmins(client, message):
    mentions = "🛡 **Admin List** 🛡\n"
    chat_id, flags = await userge.split_flags(message, '--', False)

    men_admins = '--m' in flags
    men_creator = '--mc' in flags
    show_id = '--id' in flags

    if not chat_id:
        chat_id = message.chat.id

    try:
        async for x in client.iter_chat_members(chat_id=chat_id, filter="administrators"):
            status = x.status
            first_name = x.user.first_name or ''
            last_name = x.user.last_name or ''
            username = x.user.username or None
            u_id = x.user.id

            if first_name and last_name:
                full_name = first_name + ' ' + last_name

            elif first_name:
                full_name = first_name

            elif last_name:
                full_name = last_name

            else:
                full_name = "user"

            if status == "creator":
                if men_admins or men_creator:
                    mentions += f"\n 👑 [{full_name}](tg://user?id={u_id})"

                elif username:
                    mentions += f"\n 👑 [{full_name}](https://t.me/{username})"

                else:
                    mentions += f"\n 👑 {full_name}"

                if show_id:
                    mentions += f" `{u_id}`"

            elif status == "administrator":
                if men_admins:
                    mentions += f"\n ⚜ [{full_name}](tg://user?id={u_id})"

                elif username:
                    mentions += f"\n ⚜ [{full_name}](https://t.me/{username})"

                else:
                    mentions += f"\n ⚜ {full_name}"

                if show_id:
                    mentions += f" `{u_id}`"

    except Exception as e:
        mentions += " " + str(e) + "\n"

    await message.reply(mentions, disable_web_page_preview=True)
    await message.delete()


@userge.on_cmd("ub",
    about="""__Searches Urban Dictionary for the query__

**Usage:**

    `.ub query`
    
**Exaple:**

    `.ub userge`""")
async def urban_dict(_, message):
    await message.edit("Processing...")
    query = message.matches[0].group(1)

    if query is None:
        await message.edit(f"No found any query!")
        return

    try:
        mean = urbandict.define(query)

    except HTTPError:
        await message.edit(f"Sorry, couldn't find any results for: `{query}``")
        return

    meanlen = len(mean[0]["def"]) + len(mean[0]["example"])

    if meanlen == 0:
        await message.edit(f"No result found for **{query}**")
        return

    OUTPUT = f"**Query:** `{query}`\n\n\
**Meaning:** __{mean[0]['def']}__\n\n\
**Example:**\n__{mean[0]['example']}__"

    if len(OUTPUT) >= Config.MAX_MESSAGE_LENGTH:
        await userge.send_output_as_file(
            output=OUTPUT,
            message=message,
            caption=query
        )

    else:
        await message.edit(OUTPUT)


@userge.on_cmd("tr",
    about=f"""__Translate the given text using Google Translate__

**Supported Languages:**
__{dumps(LANGUAGES, indent=4, sort_keys=True)}__

**Usage:**

--from english to sinhala--
    `.tr -en -si i am userge`

--from auto detected language to sinhala--
    `.tr -si i am userge`

--reply to message you want to translate from english to sinhala--
    `.tr -en -si`

--reply to message you want to translate from from auto detected language to sinhala--
    `.tr -si`""")
async def translateme(_, message):
    translator = Translator()

    text, flags = await userge.split_flags(message, '-')
    replied = False

    if message.reply_to_message:
        text = message.reply_to_message.text
        replied = True

    if (not replied and len(flags) < 1) or (replied and len(flags) == 0):
        await message.edit("No enough arguments found!\nuse `.help tr`")
        return

    if not text:
        await message.edit("Give a text or reply to a message to translate!\nuse `.help tr`")
        return

    if len(flags) == 2:
        src, dest = flags

    else:
        src, dest = 'auto', flags[0]

    await message.edit("Translating...")

    try:
        reply_text = translator.translate(text, dest=dest, src=src)

    except ValueError:
        await message.edit("Invalid destination language.\nuse `.help tr`")
        return

    source_lan = LANGUAGES[f'{reply_text.src.lower()}']
    transl_lan = LANGUAGES[f'{reply_text.dest.lower()}']

    OUTPUT = f"**Source ({source_lan.title()}):**`\n{text}`\n\n\
**Translation ({transl_lan.title()}):**\n`{reply_text.text}`"

    if len(OUTPUT) >= Config.MAX_MESSAGE_LENGTH:
        await userge.send_output_as_file(
            output=OUTPUT,
            message=message,
            caption="translated"
        )

    else:
        await message.edit(OUTPUT)