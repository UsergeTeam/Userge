import os
import wget
import urbandict
import speedtest
import wikipedia
import asyncio
import requests
from json import dumps
from datetime import datetime
from . import get_all_plugins
from emoji import get_emoji_regexp
from urllib.error import HTTPError
from googletrans import Translator, LANGUAGES
from search_engine_parser import GoogleSearch
from userge import userge, Config
from userge.utils import humanbytes


@userge.on_cmd("ping",
               about="__check how long it takes to ping your userbot__")
async def pingme(_, message):
    start = datetime.now()

    await message.edit('`Pong!`')

    end = datetime.now()
    ms = (end - start).microseconds / 1000

    await message.edit(f"**Pong!**\n`{ms} ms`")


@userge.on_cmd("help",
               about="__to know how to use **USERGE** commands__")
async def helpme(_, message):
    cmd = message.matches[0].group(1)
    out_str = ""

    if cmd is None:
        out_str += """**--Which command you want ?--**

**Usage**:

    `.help [command]`

**Available Commands:**\n\n"""

        for cmd in sorted(userge.get_help()):
            out_str += f"    `.{cmd}`\n"

    else:
        out = userge.get_help(cmd.lstrip('.'))
        out_str += f"`.{cmd.lstrip('.')}`\n\n{out}" if out \
            else "__command not found!__"

    await userge.send_msg(message,
                          text=out_str,
                          del_in=15)


@userge.on_cmd("s",
               about="__to search commands in **USERGE**__")
async def search(_, message):
    cmd = message.matches[0].group(1)

    if cmd is None:
        await userge.send_err(message,
                              text="Enter any keyword to search in commands")
        return

    found = '\n.'.join([i for i in sorted(userge.get_help()) \
        if cmd.lstrip('.') in i])

    if found:
        out = f"**--I found these commands:--**\n\n`.{found}`"

    else:
        out = "__command not found!__"

    await userge.send_msg(message,
                          text=out,
                          del_in=15)


@userge.on_cmd("json",
               about="""__message object to json__

**Usage:**

    reply `.json` to any message""")
async def jsonify(_, message):
    the_real_message = str(message.reply_to_message) if message.reply_to_message \
        else str(message)

    if len(the_real_message) > Config.MAX_MESSAGE_LENGTH:
        await userge.send_output_as_file(output=the_real_message,
                                         message=message,
                                         filename="json.txt",
                                         caption="Too Large")

    else:
        await message.edit(the_real_message)


@userge.on_cmd("all",
               about="__list all plugins in plugins/ path__")
async def getplugins(_, message):
    all_plugins = await get_all_plugins()

    out_str = "**--All Userge Plugins--**\n\n"

    for plugin in all_plugins:
        out_str += f"    `{plugin}`\n"

    await userge.send_msg(message,
                          text=out_str,
                          del_in=15)


@userge.on_cmd("del",
               about="__delete replied message__")
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
`-m` : __mention all admins__
`-mc` : __only mention creator__
`-id` : __show ids__

**Usage:**

    `.admins [any flag] [chatid]`""")
async def mentionadmins(_, message):
    mentions = "🛡 **Admin List** 🛡\n"
    chat_id, flags = await userge.filter_flags(message)

    men_admins = '-m' in flags
    men_creator = '-mc' in flags
    show_id = '-id' in flags

    if not chat_id:
        chat_id = message.chat.id

    try:
        async for x in userge.iter_chat_members(chat_id=chat_id, filter="administrators"):
            status = x.status
            u_id = x.user.id
            username = x.user.username or None
            full_name = (await userge.get_user_dict(u_id))['flname']

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

    await message.delete()
    await message.send_message(chat_id=message.chat.id,
                               text=mentions,
                               disable_web_page_preview=True)


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
        await userge.send_err(message,
                              text="No found any query!")
        return

    try:
        mean = urbandict.define(query)

    except HTTPError:
        await userge.send_err(message,
                              text=f"Sorry, couldn't find any results for: `{query}``")
        return

    meanlen = len(mean[0]["def"]) + len(mean[0]["example"])

    if meanlen == 0:
        await userge.send_err(message,
                              text=f"No result found for **{query}**")
        return

    OUTPUT = f"**Query:** `{query}`\n\n\
**Meaning:** __{mean[0]['def']}__\n\n\
**Example:**\n__{mean[0]['example']}__"

    if len(OUTPUT) >= Config.MAX_MESSAGE_LENGTH:
        await userge.send_output_as_file(output=OUTPUT,
                                         message=message,
                                         caption=query)

    else:
        await message.edit(OUTPUT)


@userge.on_cmd("tr",
               about=f"""__Translate the given text using Google Translate__

**Supported Languages:**
__{dumps(LANGUAGES, indent=4, sort_keys=True)}__

**Usage:**

__from english to sinhala__
    `.tr -en -si i am userge`

__from auto detected language to sinhala__
    `.tr -si i am userge`

__from auto detected language to preferred__
    `.tr i am userge`

__reply to message you want to translate from english to sinhala__
    `.tr -en -si`

__reply to message you want to translate from auto detected language to sinhala__
    `.tr -si`
    
__reply to message you want to translate from auto detected language to preferred__
    `.tr`""")
async def translateme(_, message):
    translator = Translator()

    text, flags = await userge.filter_flags(message, del_pre=True)

    if message.reply_to_message:
        text = message.reply_to_message.text

    if not text:
        await userge.send_err(message,
                              text="Give a text or reply to a message to translate!\nuse `.help tr`")
        return

    if len(flags) == 2:
        src, dest = list(flags)

    elif len(flags) == 1:
        src, dest = 'auto', list(flags)[0]

    else:
        src, dest = 'auto', Config.LANG

    text = get_emoji_regexp().sub(u'', text)

    await message.edit("Translating...")

    try:
        reply_text = translator.translate(text,
                                          dest=dest,
                                          src=src)

    except ValueError:
        await userge.send_err(message,
                              text="Invalid destination language.\nuse `.help tr`")
        return

    source_lan = LANGUAGES[f'{reply_text.src.lower()}']
    transl_lan = LANGUAGES[f'{reply_text.dest.lower()}']

    OUTPUT = f"**Source ({source_lan.title()}):**`\n{text}`\n\n\
**Translation ({transl_lan.title()}):**\n`{reply_text.text}`"

    if len(OUTPUT) >= Config.MAX_MESSAGE_LENGTH:
        await userge.send_output_as_file(output=OUTPUT,
                                         message=message,
                                         caption="translated")

    else:
        await message.edit(OUTPUT)


@userge.on_cmd("speedtest",
               about="__test your server speed__")
async def speedtst(_, message):
    await message.edit("`Running speed test . . .`")

    try:
        test = speedtest.Speedtest()
        test.get_best_server()

        await message.edit("`Performing download test . . .`")
        test.download()

        await message.edit("`Performing upload test . . .`")
        test.upload()

        test.results.share()
        result = test.results.dict()

    except Exception as e:
        await userge.send_err(message,
                              text=str(e))
        return

    path = wget.download(result['share'])

    OUTPUT = f"""**--Started at {result['timestamp']}--

Client:

ISP: `{result['client']['isp']}`
Country: `{result['client']['country']}`

Server:

Name: `{result['server']['name']}`
Country: `{result['server']['country']}, {result['server']['cc']}`
Sponsor: `{result['server']['sponsor']}`
Latency: `{result['server']['latency']}`

Ping: `{result['ping']}`
Sent: `{await humanbytes(result['bytes_sent'])}`
Received: `{await humanbytes(result['bytes_received'])}`
Download: `{await humanbytes(result['download'])}/s`
Upload: `{await humanbytes(result['upload'])}/s`**"""

    await userge.send_photo(chat_id=message.chat.id,
                            photo=path,
                            caption=OUTPUT)

    os.remove(path)
    await message.delete()


@userge.on_cmd("sd (\\d+) (.+)",
               about="""__make self-destructable messages__

**Usage:**

    `.sd [time in seconds] [text]`""")
async def selfdestruct(_, message):
    seconds = int(message.matches[0].group(1))
    text = str(message.matches[0].group(2))

    await message.edit(text)

    await asyncio.sleep(seconds)
    await message.delete()


@userge.on_cmd("google",
               about="""__do a Google search__

**Available Flags:**

    `-p` : __page of results to return (default to 1)__
    `-l` : __limit the number of returned results (defaults to 5)(max 10)__
    
**Usage:**

    `.google [flags] [query | reply to msg]`
    
**Example:**

    `.google -p4 -l10 github-userge`""")
async def gsearch(_, message):
    await message.edit("Processing ...")

    query, flags = await userge.filter_flags(message)

    page = int(flags.get('-p', 1))
    limit = int(flags.get('-l', 5))

    if message.reply_to_message:
        query = message.reply_to_message.text

    if not query:
        await userge.send_err(message,
                              text="Give a query or reply to a message to google!")
        return

    try:
        gsearch = GoogleSearch()
        gresults = gsearch.search(query, page)

    except Exception as e:
        await userge.send_err(message,
                              text=str(e))
        return

    OUTPUT = ""

    for i in range(limit):
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            OUTPUT += f"[{title}]({link})\n"
            OUTPUT += f"`{desc}`\n\n"

        except IndexError:
            break

    OUTPUT = f"**Google Search:**\n`{query}`\n\n**Results:**\n{OUTPUT}"

    if len(OUTPUT) >= Config.MAX_MESSAGE_LENGTH:
        await userge.send_output_as_file(output=OUTPUT,
                                         message=message,
                                         caption=query)

    else:
        await message.edit(OUTPUT, disable_web_page_preview=True)


@userge.on_cmd("wiki",
               about="""__do a Wikipedia search__

**Available Flags:**

    `-l` : __limit the number of returned results (defaults to 5)__

**Usage:**

    `.wiki [flags] [query | reply to msg]`
    
**Example:**

    `.wiki -l5 userge`""")
async def wiki_pedia(_, message):
    await message.edit("Processing ...")

    query, flags = await userge.filter_flags(message)

    limit = int(flags.get('-l', 5))

    if message.reply_to_message:
        query = message.reply_to_message.text

    if not query:
        await userge.send_err(message,
                              text="Give a query or reply to a message to wikipedia!")
        return

    try:
        wikipedia.set_lang("en")
        results = wikipedia.search(query)

    except Exception as e:
        await userge.send_err(message,
                              text=str(e))
        return

    OUTPUT = ""

    for i, s in enumerate(results, start=1):
        page = wikipedia.page(s)
        url = page.url
        OUTPUT += f"🌏 [{s}]({url})\n"

        if i == limit:
            break

    OUTPUT = f"**Wikipedia Search:**\n`{query}`\n\n**Results:**\n{OUTPUT}"

    if len(OUTPUT) >= Config.MAX_MESSAGE_LENGTH:
        await userge.send_output_as_file(output=OUTPUT,
                                         message=message,
                                         caption=query)

    else:
        await message.edit(OUTPUT,
                           disable_web_page_preview=True)


@userge.on_cmd("head",
               about="""__View headers in URL__

**Available Flags:**

    `-r` : __allow redirects__
    `-s` : __allow streams__
    `-t` : __request timeout__

**Usage:**

    `.head [flags] [url]`
    
**Example:**

    `.head -r -s -t5 https://www.google.com`""")
async def req_head(_, message):
    await message.edit("Processing ...")

    link, flags = await userge.filter_flags(message)
    
    red = True if '-r' in flags else False
    stm = True if '-s' in flags else False
    tout = int(flags.get('-t', 3))

    if not link:
        await userge.send_err(message,
                              text="Please give me a link link!")
        return

    try:
        cd = requests.head(url=link,
                           stream=stm,
                           allow_redirects=red,
                           timeout=tout)

    except Exception as e:
        await userge.send_err(message,
                              text=str(e))
        return

    OUTPUT = f"**url**: `{link}`\n**http_status_code**: __{cd.status_code}__\n**headers**:\n"

    for k, v in cd.headers.items():
        OUTPUT += f"    __{k.lower()}__ : `{v}`\n"

    if len(OUTPUT) >= Config.MAX_MESSAGE_LENGTH:
        await userge.send_output_as_file(output=OUTPUT,
                                         message=message,
                                         caption=link)

    else:
        await message.edit(OUTPUT,
                           disable_web_page_preview=True)
