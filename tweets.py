""" Fun Stickers for Tweet """

# By @Krishna_Singhal

import os
import re
import requests

from PIL import Image
from validators.url import url

from userge import userge, Config, Message, deEmojify

CONVERTED_IMG = Config.DOWN_PATH + "img.png"
CONVERTED_STIKR = Config.DOWN_PATH + "sticker.webp"

@userge.on_cmd("trump", about={
    'header': "Custom Sticker of Trump Tweet",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}trump [text | reply to text]"})
async def trump_tweet(msg: Message):
    """ Fun sticker of Trump Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("Trump Need some Text for Tweet 🙄")
        return
    await msg.edit("```Requesting trump to tweet... 😃```")
    await _tweets(msg, text, type_="trumptweet")


@userge.on_cmd("modi", about={
    'header': "Custom Sticker of Modi Tweet",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}modi [text | reply to text]"})
async def modi_tweet(msg: Message):
    """ Fun Sticker of Modi Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("Modi Need some Text for Tweet 😗")
        return
    await msg.edit("```Requesting Modi to tweet... 😉```")
    await _tweets(msg, text, "narendramodi")


@userge.on_cmd("cmm", about={
    'header': "Custom Sticker of Change My Mind",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}cmm [text | reply to text]"})
async def Change_My_Mind(msg: Message):
    """ Custom Sticker or Banner of Change My Mind """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("Need some Text to Change My Mind 🙂")
        return
    await msg.edit("```Writing Banner of Change My Mind 😁```")
    await _tweets(msg, text, type_="changemymind")


@userge.on_cmd("kanna", about={
    'header': "Custom text Sticker of kanna",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}kanna [text | reply to text]"})
async def kanna(msg: Message):
    """ Fun sticker of Kanna """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("Kanna Need some text to Write 😚")
        return
    await msg.edit("```Kanna is writing for You 😀```")
    await _tweets(msg, text, type_="kannagen")


@userge.on_cmd("carry", about={
    'header': "Custom text Sticker of Carryminati",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}carry [text | reply to text]"})
async def carry_minati(msg: Message):
    """ Fun Sticker of Carryminati Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("Carry Need some text to Write 😚")
        return
    await msg.edit("```Carry Minati is writing for You 😀```")
    await _tweets(msg, text, "carryminati")


@userge.on_cmd("tweet", about={
    'header': "Tweet With Custom text Sticker",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}tweet Text , Username\n"
             "{tr}tweet Text\n"
             "{tr}tweet [Text | with reply to User]"})
async def tweet(msg: Message):
    """ Tweet with your own Username """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("Give Me some text to Tweet 😕")
        return
    username = ''
    if ',' in text:
        text, username = text.split(',')
    if not username:
        if replied:
            username = replied.from_user.username or replied.from_user.first_name
        else:
            username = msg.from_user.username or msg.from_user.first_name
    await msg.edit("```Creating a Tweet Sticker 😏```")
    await _tweets(msg, text.strip(), username.strip())

async def _tweets(msg: Message, text: str, username: str = '', type_: str = "tweet") -> None:
    api_url = f"https://nekobot.xyz/api/imagegen?type={type_}&text={deEmojify(text)}"
    if username:
        api_url += f"&username={deEmojify(username)}"
    res = requests.get(api_url).json()
    tweets_ = res.get("message")
    if not url(tweets_):
        await msg.err("Invalid Syntax, Exiting...")
        return
    tmp_file = Config.DOWN_PATH + "temp.png"
    with open(tmp_file, "wb") as t_f:
        t_f.write(requests.get(tweets_).content)
    img = Image.open(tmp_file)
    img.save(CONVERTED_IMG)
    img.save(CONVERTED_STIKR)
    await msg.delete()
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else None
    if '-s' in msg.flags:
        await msg.client.send_sticker(chat_id=msg.chat.id,
                                      sticker=CONVERTED_STIKR,
                                      reply_to_message_id=msg_id)
    else:
        await msg.client.send_photo(chat_id=msg.chat.id,
                                    photo=CONVERTED_IMG,
                                    reply_to_message_id=msg_id)
    os.remove(tmp_file)
    os.remove(CONVERTED_IMG)
    os.remove(CONVERTED_STIKR)

    
    
@userge.on_cmd("clb", about={
    'header': "Custom text Sticker for Any Celebrity",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}clb [short_name | text or reply to text]",
    'Fonts': "<code>Check this</code> "
    "<a href='https://telegra.ph/Short-Celeb-Names-08-07'>short_name</a>"
    " <code>to know Celeb Names</code>"})
    
async def celeb_(message: Message):
    """ Fun Sticker Celeb Tweet """

    CELEBS = {
        "salman": "BeingSalmanKhan",
        "srk": "iamsrk",
        "ab": "SrBachchan",
        "ambani": "Asliambani",
        "jio": "reliancejio",
        "telegram": "telegram",
        "whatsapp": "WhatsApp",
        "ananya": "ananyapandayy",
        "sonakshi": "Aslisonagold",
        "sonam": "sonamakapoor",
        "johar": "karanjohar",
        "yogi": "myogiadityanath",
        "ramdev": "yogrishiramdev",
        "arnab": "ArnabGoswamiRTV",
        "rahul": "RahulGandhi",
        "rajni" : "rajinikanth",
        "apple" : "apple",
        "fb" : "facebook",
        "bjp" : "bjp4india",
        "yt" : "youtube",
        "kaiara" : "advani_kiara",
        "rdj" : "RobertDowneyJr",
        "chris" : "chrishhemsworth",
        "netflix" : "netflix",
        "setu" : "Arogyasetu",
        "ph" : "pornhub",
        "osama" : "ItstherealOsama",
        "hashmi" : "emraanhashmi",
        "android" : "Android",
        "ht" : "htTweets",
        "zee" : "ZeeNews"
    }

    replied = message.reply_to_message
    if replied:
        if "," in message.input_str:
            celeb_name, msg_text = message.input_str.split(',')
            celeb_name = celeb_name.strip()
            comment = msg_text or replied.text
        else:
            celeb_name = message.input_str
            comment = replied.text
        if not celeb_name and comment:
            await message.err("```Input not found! Give celeb name and text, See Help for more!...```", del_in=3)
            return
    else:
        if "," in message.input_str:
                celeb_name, msg_text = message.input_str.split(',')
                celeb_name = celeb_name.strip()
                comment = msg_text
        else:
            await message.err("```Input not found! See Help...```", del_in=3)
            return
    celebrity = CELEBS[celeb_name]
    if not celebrity:
       await message.err("```Not A Valid Celeb Name```", del_in=3)
       return 
    await message.edit(f"```{celeb_name} is writing for You 😀```")
    await _tweets(message, comment, celebrity)

    
