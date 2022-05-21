""" Fun Stickers for Tweet """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

# By @Krishna_Singhal

import os

import requests
from PIL import Image
from emoji import get_emoji_regexp
from validators.url import url

from userge import userge, config, Message

CONVERTED_IMG = config.Dynamic.DOWN_PATH + "img.png"


@userge.on_cmd("trump", about={
    'header': "Custom Sticker of Trump Tweet",
    'usage': "{tr}trump [text | reply to text]"})
async def trump_tweet(msg: Message):
    """ Fun sticker of Trump Tweet """
    replied = msg.reply_to_message
    text = msg.input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("Trump Need some Text for Tweet 🙄")
        return
    await msg.edit("```Requesting trump to tweet... 😃```")
    await _tweets(msg, text, type_="trumptweet")


@userge.on_cmd("modi", about={
    'header': "Custom Sticker of Modi Tweet",
    'usage': "{tr}modi [text | reply to text]"})
async def modi_tweet(msg: Message):
    """ Fun Sticker of Modi Tweet """
    replied = msg.reply_to_message
    text = msg.input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("Modi Need some Text for Tweet 😗")
        return
    await msg.edit("```Requesting Modi to tweet... 😉```")
    await _tweets(msg, text, "narendramodi")


@userge.on_cmd("cmm", about={
    'header': "Custom Sticker of Change My Mind",
    'usage': "{tr}cmm [text | reply to text]"})
async def Change_My_Mind(msg: Message):
    """ Custom Sticker or Banner of Change My Mind """
    replied = msg.reply_to_message
    text = msg.input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("Need some Text to Change My Mind 🙂")
        return
    await msg.edit("```Writing Banner of Change My Mind 😁```")
    await _tweets(msg, text, type_="changemymind")


@userge.on_cmd("kanna", about={
    'header': "Custom text Sticker of kanna",
    'usage': "{tr}kanna [text | reply to text]"})
async def kanna(msg: Message):
    """ Fun sticker of Kanna """
    replied = msg.reply_to_message
    text = msg.input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("Kanna Need some text to Write 😚")
        return
    await msg.edit("```Kanna is writing for You 😀```")
    await _tweets(msg, text, type_="kannagen")


@userge.on_cmd("carry", about={
    'header': "Custom text Sticker of Carryminati",
    'usage': "{tr}carry [text | reply to text]"})
async def carry_minati(msg: Message):
    """ Fun Sticker of Carryminati Tweet """
    replied = msg.reply_to_message
    text = msg.input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("Carry Need some text to Write 😚")
        return
    await msg.edit("```Carry Minati is writing for You 😀```")
    await _tweets(msg, text, "carryminati")


@userge.on_cmd("tweet", about={
    'header': "Tweet With Custom text Sticker",
    'usage': "{tr}tweet username text\n"
             "{tr}tweet text [reply to user]\n"
             "{tr}tweet [reply]"})
async def tweet(msg: Message):
    """ Create Tweets of given celebrities """
    username, text = msg.extract_user_and_text
    if not (username or text):
        await msg.err("`input not found!`")
        return
    await msg.edit("```Creating a Tweet Sticker 😏```")
    await _tweets(msg, text, username)


async def _tweets(msg: Message, text: str, username: str = '', type_: str = "tweet") -> None:
    api_url = f"https://nekobot.xyz/api/imagegen?type={type_}"
    api_url += f"&text={get_emoji_regexp().sub(b'', text)}"
    if username:
        api_url += f"&username={get_emoji_regexp().sub(b'', username)}"
    res = requests.get(api_url).json()
    tweets_ = res.get("message")
    if not url(tweets_):
        await msg.err("Invalid Syntax, Exiting...")
        return
    tmp_file = config.Dynamic.DOWN_PATH + "temp.png"
    with open(tmp_file, "wb") as t_f:
        t_f.write(requests.get(tweets_).content)
    img = Image.open(tmp_file)
    img.save(CONVERTED_IMG)
    await msg.delete()
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else None
    await msg.client.send_photo(chat_id=msg.chat.id,
                                photo=CONVERTED_IMG,
                                reply_to_message_id=msg_id)
    os.remove(tmp_file)
    os.remove(CONVERTED_IMG)
