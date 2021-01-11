""" enjoy memes """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import time
import asyncio
from re import sub
from collections import deque
from random import choice, getrandbits, randint

import wget
import requests
from cowpy import cow

from userge import userge, Message


@userge.on_cmd(r"(?:Kek|:/)$",
               about={'header': "Check yourself, hint: `:/`"}, name='Kek',
               trigger='', allow_via_bot=False)
async def kek_(message: Message):
    """kek"""
    kek = ["/", "\\"]
    for i in range(1, 9):
        time.sleep(0.3)
        await message.try_to_edit(":" + kek[i % 2])


@userge.on_cmd(r"(?:Lol|-_-)$",
               about={'header': "Check yourself, hint: `-_-`"}, name='Lol',
               trigger='', allow_via_bot=False)
async def lol_(message: Message):
    """lol"""
    lol = "-_ "
    for i in range(9):
        if i % 3 == 0:
            lol = "-_ "
        lol = lol[:-1] + "_-"
        await message.try_to_edit(lol, parse_mode="html")


@userge.on_cmd(r"(?:Fun|;_;)$",
               about={'header': "Check yourself, hint: `;_;`"}, name="Fun",
               trigger='', allow_via_bot=False)
async def fun_(message: Message):
    """fun"""
    fun = ";_ "
    for i in range(9):
        if i % 3 == 0:
            fun = ";_ "
        fun = fun[:-1] + "_;"
        await message.try_to_edit(fun, parse_mode="html")


@userge.on_cmd("Oof$", about={'header': "Ooooof"},
               trigger='', allow_via_bot=False)
async def Oof_(message: Message):
    """Oof"""
    Oof = "Oo "
    for _ in range(6):
        Oof = Oof[:-1] + "of"
        await message.try_to_edit(Oof)


@userge.on_cmd("Hmm$", about={'header': "Hmmmmm"},
               trigger='', allow_via_bot=False)
async def Hmm_(message: Message):
    """Hmm"""
    Hmm = "Hm "
    for _ in range(4):
        Hmm = Hmm[:-1] + "mm"
        await message.try_to_edit(Hmm)


async def check_and_send(message: Message, *args, **kwargs):
    replied = message.reply_to_message
    if replied:
        await asyncio.gather(
            message.delete(),
            replied.reply(*args, **kwargs)
        )
    else:
        await message.edit(*args, **kwargs)


@userge.on_cmd("fp$", about={'header': "Facepalm :P"})
async def facepalm_(message: Message):
    """facepalm_"""
    await check_and_send(message, "🤦‍♂")


@userge.on_cmd("cry$", about={'header': "y u du dis, i cri"})
async def cry_(message: Message):
    """cry"""
    await check_and_send(message, choice(CRI), parse_mode="html")


@userge.on_cmd("insult$", about={'header': "Check yourself ;)"})
async def insult_(message: Message):
    """insult"""
    await check_and_send(message, choice(INSULT_STRINGS), parse_mode="html")


@userge.on_cmd("hi", about={
    'header': "Greet everyone!",
    'usage': "{tr}hi\n{tr}hi [emoji | character]\n{tr}hi [emoji | character] [emoji | character]"})
async def hi_(message: Message):
    """hi"""
    input_str = message.input_str
    if not input_str:
        await message.edit(choice(HELLOSTR), parse_mode="html")
    else:
        args = input_str.split()
        if len(args) == 2:
            paytext, filler = args
        else:
            paytext = args[0]
            filler = choice(EMOJIS)
        pay = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
            paytext * 2 + filler * 4 + paytext * 2 + filler * 2 + paytext * 2,
            paytext * 2 + filler * 4 + paytext * 2 + filler * 2 + paytext * 2,
            paytext * 2 + filler * 4 + paytext * 2 + filler * 4,
            paytext * 2 + filler * 4 + paytext * 2 + filler * 4,
            paytext * 2 + filler * 4 + paytext * 2 + filler * 2 + paytext * 2,
            paytext * 8 + filler * 2 + paytext * 2,
            paytext * 8 + filler * 2 + paytext * 2,
            paytext * 2 + filler * 4 + paytext * 2 + filler * 2 + paytext * 2,
            paytext * 2 + filler * 4 + paytext * 2 + filler * 2 + paytext * 2,
            paytext * 2 + filler * 4 + paytext * 2 + filler * 2 + paytext * 2,
            paytext * 2 + filler * 4 + paytext * 2 + filler * 2 + paytext * 2,
            paytext * 2 + filler * 4 + paytext * 2 + filler * 2 + paytext * 2)
        await message.edit(pay)


@userge.on_cmd("react", about={
    'header': "Make your userbot react to everything",
    'types': ['happy', 'thinking', 'waving', 'wtf', 'love', 'confused', 'dead', 'sad', 'dog'],
    'usage': "{tr}react [type]",
    'examples': ["{tr}react", "{tr}react dead"]})
async def react_(message: Message):
    """react"""
    type_ = message.input_str
    if "happy" in type_:
        out = choice(HAPPY)
    elif "thinking" in type_:
        out = choice(THINKING)
    elif "waving" in type_:
        out = choice(WAVING)
    elif "wtf" in type_:
        out = choice(WTF)
    elif "love" in type_:
        out = choice(LOVE)
    elif "confused" in type_:
        out = choice(CONFUSED)
    elif "dead" in type_:
        out = choice(DEAD)
    elif "sad" in type_:
        out = choice(SAD)
    elif "dog" in type_:
        out = choice(DOG)
    else:
        out = choice(FACEREACTS)
    await check_and_send(message, out, parse_mode="html")


@userge.on_cmd("shg$", about={'header': "Shrug at it !!"})
async def shrugger(message: Message):
    """shrugger"""
    await check_and_send(message, choice(SHGS), parse_mode="html")


@userge.on_cmd("chase$", about={'header': "You better start running"})
async def chase_(message: Message):
    """chase"""
    await check_and_send(message, choice(CHASE_STR), parse_mode="html")


@userge.on_cmd("run$", about={'header': "Let Me Run, run, RUNNN!"})
async def run_(message: Message):
    """run"""
    await check_and_send(message, choice(RUNS_STR), parse_mode="html")


@userge.on_cmd("metoo$", about={'header': "Haha yes"})
async def metoo_(message: Message):
    """metoo"""
    await check_and_send(message, choice(METOOSTR), parse_mode="html")


@userge.on_cmd("10iq$", about={'header': "You retard !!"}, name="10iq")
async def iqless(message: Message):
    """iqless"""
    await check_and_send(message, "♿")


@userge.on_cmd("moon$", about={'header': "kensar moon animation"})
async def moon_(message: Message):
    """moon"""
    deq = deque(list("🌗🌘🌑🌒🌓🌔🌕🌖"))
    try:
        for _ in range(32):
            await asyncio.sleep(0.1)
            await message.edit("".join(deq))
            deq.rotate(1)
    except Exception:
        await message.delete()


@userge.on_cmd("clock$", about={'header': "kensar clock animation"})
async def clock_(message: Message):
    """clock"""
    deq = deque(list("🕚🕙🕘🕗🕖🕕🕔🕓🕒🕑🕐🕛"))
    try:
        for _ in range(36):
            await asyncio.sleep(0.1)
            await message.edit("".join(deq))
            deq.rotate(1)
    except Exception:
        await message.delete()


@userge.on_cmd("bt$", about={
    'header': "Believe me, you will find this useful",
    'usage': "{tr}bt [reply to msg]"})
async def bluetext(message: Message):
    """bluetext"""
    if message.reply_to_message:
        await message.edit(
            "/BLUETEXT /MUST /CLICK.\n"
            "/ARE /YOU /A /STUPID /ANIMAL /WHICH /IS /ATTRACTED /TO /COLOURS?")


@userge.on_cmd("f (.+)", about={
    'header': "Pay Respects",
    'usage': "{tr}f [emoji | character]"})
async def payf_(message: Message):
    """payf"""
    paytext = message.input_str
    pay = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        paytext * 8, paytext * 8, paytext * 2, paytext * 2, paytext * 2,
        paytext * 6, paytext * 6, paytext * 2, paytext * 2, paytext * 2,
        paytext * 2, paytext * 2)
    await message.edit(pay)


@userge.on_cmd("clap", about={
    'header': "Praise people!",
    'usage': "{tr}clap [input | reply to msg]"})
async def clap_(message: Message):
    """clap"""
    input_str = message.input_or_reply_str
    if not input_str:
        await message.edit("`Hah, I don't clap pointlessly!`")
        return
    reply_text = "👏 "
    reply_text += input_str.replace(" ", " 👏 ")
    reply_text += " 👏"
    await message.edit(reply_text)


@userge.on_cmd("(\\w+)say (.+)", about={
    'header': "cow which says things",
    'usage': "{tr}[any cowacter]say [text]",
    'cowacters': f"`{'`,    `'.join(cow.COWACTERS)}`"}, name="cowsay")
async def cowsay_(message: Message):
    """cowsay"""
    arg = message.matches[0].group(1).lower()
    text = message.matches[0].group(2)
    if arg == "cow":
        arg = "default"
    if arg not in cow.COWACTERS:
        await message.err("cowacter not found!")
        return
    cheese = cow.get_cow(arg)
    cheese = cheese()
    await message.edit(f"`{cheese.milk(text).replace('`', '´')}`")


@userge.on_cmd("coinflip", about={
    'header': "Flip a coin !!",
    'usage': "{tr}coinflip [heads | tails]"})
async def coin_(message: Message):
    """coin"""
    r = choice(["heads", "tails"])
    input_str = message.input_str
    if not input_str:
        return
    input_str = input_str.lower()
    if r == "heads":
        if input_str == "heads":
            await message.edit(
                "The coin landed on: **Heads**.\nYou were correct.")
        elif input_str == "tails":
            await message.edit(
                "The coin landed on: **Heads**.\nYou weren't correct, try again ...")
        else:
            await message.edit("The coin landed on: **Heads**.")
    elif r == "tails":
        if input_str == "tails":
            await message.edit(
                "The coin landed on: **Tails**.\nYou were correct.")
        elif input_str == "heads":
            await message.edit(
                "The coin landed on: **Tails**.\nYou weren't correct, try again ...")
        else:
            await message.edit("The coin landed on: **Tails**.")


@userge.on_cmd("slap", about={
    'header': "reply to slap them with random objects !!",
    'usage': "{tr}slap [input | reply to msg]"}, allow_channels=False)
async def slap_(message: Message):
    """slap"""
    u_id = message.input_str
    if message.reply_to_message:
        u_id = message.reply_to_message.from_user.id
    if not u_id:
        await message.err("no input found!")
        return
    info_dict = await message.client.get_user_dict(u_id)
    temp = choice(SLAP_TEMPLATES)
    item = choice(ITEMS)
    hit = choice(HIT)
    throw = choice(THROW)
    where = choice(WHERE)
    caption = "..." + temp.format(victim=info_dict['mention'],
                                  item=item, hits=hit,
                                  throws=throw, where=where)
    try:
        await message.edit(caption)
    except Exception:
        await message.edit(
            "`Can't slap this person, need to fetch some sticks and stones !!`")


@userge.on_cmd("(yes|no|maybe|decide)$", about={
    'header': "Make a quick decision",
    'flags': {'-gif': "for gif"},
    'examples': ['{tr}decide', '{tr}yes', '{tr}no', '{tr}maybe']}, name="decide")
async def decide_(message: Message):
    """decide"""
    decision = message.matches[0].group(1).lower()
    await message.edit("hmm...")
    if decision != "decide":
        r = requests.get(f"https://yesno.wtf/api?force={decision}").json()
    else:
        r = requests.get("https://yesno.wtf/api").json()
    path = wget.download(r["image"])
    chat_id = message.chat.id
    message_id = message.reply_to_message.message_id if message.reply_to_message else None
    await message.delete()
    if '-gif' in message.flags:
        await message.client.send_animation(chat_id=chat_id,
                                            animation=path,
                                            caption=str(r["answer"]).upper(),
                                            reply_to_message_id=message_id)
    else:
        await message.client.send_photo(chat_id=chat_id,
                                        photo=path,
                                        caption=str(r["answer"]).upper(),
                                        reply_to_message_id=message_id)
    os.remove(path)


@userge.on_cmd("cp", about={
    'header': "Copypasta the famous meme",
    'usage': "{tr}cp [input | reply to msg]"})
async def copypasta(message: Message):
    """copypasta"""
    input_str = message.input_or_reply_str
    if not input_str:
        await message.edit("`😂🅱️IvE👐sOME👅text👅for✌️Me👌tO👐MAkE👀iT💞funNy!💦`")
        return
    reply_text = choice(EMOJIS)
    # choose a random character in the message to be substituted with 🅱️
    b_char = choice(input_str).lower()
    for owo in input_str:
        if owo == " ":
            reply_text += choice(EMOJIS)
        elif owo in EMOJIS:
            reply_text += owo
            reply_text += choice(EMOJIS)
        elif owo.lower() == b_char:
            reply_text += "🅱️"
        else:
            if bool(getrandbits(1)):
                reply_text += owo.upper()
            else:
                reply_text += owo.lower()
    reply_text += choice(EMOJIS)
    await message.edit(reply_text)


@userge.on_cmd("vapor", about={
    'header': "Vaporize everything!",
    'usage': "{tr}vapor [input | reply to msg]"})
async def vapor_(message: Message):
    """vapor"""
    input_str = message.input_or_reply_str
    if not input_str:
        await message.edit("`Ｇｉｖｅ ｓｏｍｅ ｔｅｘｔ ｆｏｒ ｖａｐｏｒ！`")
        return
    reply_text = []
    for charac in input_str:
        if 0x21 <= ord(charac) <= 0x7F:
            reply_text.append(chr(ord(charac) + 0xFEE0))
        elif ord(charac) == 0x20:
            reply_text.append(chr(0x3000))
        else:
            reply_text.append(charac)
    await message.edit("".join(reply_text))


@userge.on_cmd("str", about={
    'header': "Stretch it",
    'usage': "{tr}str [input | reply to msg]"})
async def stretch(message: Message):
    """stretch"""
    input_str = message.input_or_reply_str
    if not input_str:
        await message.edit("`GiiiiiiiB sooooooomeeeeeee teeeeeeext!`")
        return
    await message.edit(
        sub(r"([aeiouAEIOUａｅｉｏｕＡＥＩＯＵаеиоуюяыэё])", (r"\1" * randint(3, 10)), input_str))


@userge.on_cmd("zal", about={
    'header': "Invoke the feeling of chaos",
    'usage': "{tr}zal [input | reply to msg]"})
async def zal_(message: Message):
    """zal"""
    input_str = message.input_or_reply_str
    if not input_str:
        await message.edit("`gͫ ̆ i̛ ̺ v͇̆ ȅͅ   a̢ͦ   s̴̪ c̸̢ ä̸ rͩͣ y͖͞   t̨͚ é̠ x̢͖  t͔͛`")
        return
    reply_text = []
    for charac in input_str:
        if not charac.isalpha():
            reply_text.append(charac)
            continue
        for _ in range(0, 3):
            randint_ = randint(0, 2)
            if randint_ == 0:
                charac = charac.strip() + choice(ZALG_LIST[0]).strip()
            elif randint_ == 1:
                charac = charac.strip() + choice(ZALG_LIST[1]).strip()
            else:
                charac = charac.strip() + choice(ZALG_LIST[2]).strip()
        reply_text.append(charac)
    await message.edit("".join(reply_text))


@userge.on_cmd("owo", about={
    'header': "UwU",
    'usage': "{tr}owo [input | reply to msg]"})
async def owo_(message: Message):
    """owo"""
    input_str = message.input_or_reply_str
    if not input_str:
        await message.edit("` UwU no text given! `")
        return
    reply_text = sub(r"([rl])", "w", input_str)
    reply_text = sub(r"([RL])", "W", reply_text)
    reply_text = sub(r"n([aeiou])", r"ny\1", reply_text)
    reply_text = sub(r"N([aeiouAEIOU])", r"Ny\1", reply_text)
    reply_text = sub(r"!", " " + choice(UWUS), reply_text)
    reply_text = reply_text.replace("ove", "uv")
    reply_text += " " + choice(UWUS)
    await message.edit(reply_text)


@userge.on_cmd("mock", about={
    'header': "Do it and find the real fun",
    'usage': "{tr}mock [input | reply to msg]"})
async def mock_(message: Message):
    """mock"""
    input_str = message.input_or_reply_str
    if not input_str:
        await message.edit("`gIvE sOMEtHInG tO MoCk!`")
        return
    reply_text = []
    for charac in input_str:
        if charac.isalpha() and randint(0, 1):
            to_app = charac.upper() if charac.islower() else charac.lower()
            reply_text.append(to_app)
        else:
            reply_text.append(charac)
    await message.edit("".join(reply_text))


@userge.on_cmd("lfy", about={
    'header': "Let me Google that for you real quick !!",
    'usage': "{tr}lfy [query | reply to msg]"})
async def lfy_(message: Message):
    """lfy_"""
    query = message.input_or_reply_str
    if not query:
        await message.edit("`gIvE sOMEtHInG tO lFy!`")
        return
    query_encoded = query.replace(" ", "+")
    lfy_url = f"http://lmgtfy.com/?s=g&iie=1&q={query_encoded}"
    payload = {'format': 'json', 'url': lfy_url}
    r = requests.get('http://is.gd/create.php', params=payload)
    await message.edit(f"Here you are, help yourself.\n[{query}]({r.json()['shorturl']})")


@userge.on_cmd("scam", about={
    'header': "Create fake chat actions, for fun.",
    'available actions': [
        'typing (default)', 'playing', 'upload_photo', 'upload_video',
        'upload_audio', 'upload_document', 'upload_video_note',
        'record_video', 'record_audio', 'record_video_note',
        'find_location', 'choose_contact'],
    'usage': "{tr}scam\n{tr}scam [action]\n{tr}scam [time]\n{tr}scam [action] [time]"})
async def scam_(message: Message):
    """scam"""
    options = ('typing', 'upload_photo', 'record_video', 'upload_video', 'record_audio',
               'upload_audio', 'upload_document', 'find_location', 'record_video_note',
               'upload_video_note', 'choose_contact', 'playing')
    input_str = message.input_str
    args = input_str.split()
    if len(args) == 0:  # Let bot decide action and time
        scam_action = choice(options)
        scam_time = randint(30, 60)
    elif len(args) == 1:  # User decides time/action, bot decides the other.
        try:
            scam_action = str(args[0]).lower()
            scam_time = randint(30, 60)
        except ValueError:
            scam_action = choice(options)
            scam_time = int(args[0])
    elif len(args) == 2:  # User decides both action and time
        scam_action = str(args[0]).lower()
        scam_time = int(args[1])
    else:
        await message.edit("`Invalid Syntax !!`")
        return
    try:
        if scam_time > 0:
            chat_id = message.chat.id
            await message.delete()
            count = 0
            while count <= scam_time:
                await message.client.send_chat_action(chat_id, scam_action)
                await asyncio.sleep(5)
                count += 5
    except Exception:
        await message.delete()


@userge.on_cmd("try", about={
    'header': "send dart or dice randomly",
    'usage': "{tr}try [send to chat or anyone]"})
async def dice_gen(message: Message):
    """send dice"""
    random_emo = choice(DICE_EMO)
    await message.client.send_dice(message.chat.id, random_emo)
    await message.delete()


THROW = ("throws", "flings", "chucks", "hurls")

HIT = ("hits", "whacks", "slaps", "smacks", "bashes")

WHERE = ("in the chest", "on the head", "on the butt", "on the crotch")

METOOSTR = (
    "Me too thanks", "Haha yes, me too", "Same lol", "Me irl", "Same here", "Haha yes", "Me rn")

HELLOSTR = (
    "Hi !", "‘Ello, gov'nor!", "What’s crackin’?", "‘Sup, homeslice?", "Howdy, howdy ,howdy!",
    "Hello, who's there, I'm talking.", "You know who this is.", "Yo!", "Whaddup.",
    "Greetings and salutations!", "Hello, sunshine!", "Hey, howdy, hi!",
    "What’s kickin’, little chicken?", "Peek-a-boo!", "Howdy-doody!",
    "Hey there, freshman!", "I come in peace!", "Ahoy, matey!", "Hiya!")

ITEMS = (
    "cast iron skillet", "large trout", "baseball bat", "cricket bat", "wooden cane", "nail",
    "printer", "shovel", "pair of trousers", "CRT monitor", "diamond sword", "baguette",
    "physics textbook", "toaster", "portrait of Richard Stallman", "television", "mau5head",
    "five ton truck", "roll of duct tape", "book", "laptop", "old television",
    "sack of rocks", "rainbow trout", "cobblestone block", "lava bucket", "rubber chicken",
    "spiked bat", "gold block", "fire extinguisher", "heavy rock", "chunk of dirt",
    "beehive", "piece of rotten meat", "bear", "ton of bricks")

RUNS_STR = (
    "Runs to Thanos..",
    "Runs far, far away from earth..",
    "Running faster than Bolt coz i'mma userbot !!",
    "Runs to Marie..",
    "This Group is too cancerous to deal with.",
    "Cya bois",
    "Kys",
    "I go away",
    "I am just walking off, coz me is too fat.",
    "I Fugged off!",
    "Will run for chocolate.",
    "I run because I really like food.",
    "Running...\nbecause dieting is not an option.",
    "Wicked fast runnah",
    "If you wanna catch me, you got to be fast...\nIf you wanna stay with me, "
    "you got to be good...\nBut if you wanna pass me...\nYou've got to be kidding.",
    "Anyone can run a hundred meters, it's the next forty-two thousand and two hundred that count.",
    "Why are all these people following me?",
    "Are the kids still chasing me?",
    "Running a marathon...there's an app for that.")

SLAP_TEMPLATES = (
    "{hits} {victim} with a {item}.",
    "{hits} {victim} in the face with a {item}.",
    "{hits} {victim} around a bit with a {item}.",
    "{throws} a {item} at {victim}.",
    "grabs a {item} and {throws} it at {victim}'s face.",
    "{hits} a {item} at {victim}.", "{throws} a few {item} at {victim}.",
    "grabs a {item} and {throws} it in {victim}'s face.",
    "launches a {item} in {victim}'s general direction.",
    "sits on {victim}'s face while slamming a {item} {where}.",
    "starts slapping {victim} silly with a {item}.",
    "pins {victim} down and repeatedly {hits} them with a {item}.",
    "grabs up a {item} and {hits} {victim} with it.",
    "starts slapping {victim} silly with a {item}.",
    "holds {victim} down and repeatedly {hits} them with a {item}.",
    "prods {victim} with a {item}.",
    "picks up a {item} and {hits} {victim} with it.",
    "ties {victim} to a chair and {throws} a {item} at them.",
    "{hits} {victim} {where} with a {item}.",
    "ties {victim} to a pole and whips them {where} with a {item}."
    "gave a friendly push to help {victim} learn to swim in lava.",
    "sent {victim} to /dev/null.", "sent {victim} down the memory hole.",
    "beheaded {victim}.", "threw {victim} off a building.",
    "replaced all of {victim}'s music with Nickelback.",
    "spammed {victim}'s email.", "made {victim} a knuckle sandwich.",
    "slapped {victim} with pure nothing.",
    "hit {victim} with a small, interstellar spaceship.",
    "quickscoped {victim}.", "put {victim} in check-mate.",
    "RSA-encrypted {victim} and deleted the private key.",
    "put {victim} in the friendzone.",
    "slaps {victim} with a DMCA takedown request!")

CHASE_STR = (
    "Where do you think you're going?",
    "Huh? what? did they get away?",
    "ZZzzZZzz... Huh? what? oh, just them again, nevermind.",
    "Get back here!",
    "Not so fast...",
    "Look out for the wall!",
    "Don't leave me alone with them!!",
    "You run, you die.",
    "Jokes on you, I'm everywhere",
    "You're gonna regret that...",
    "You could also try /kickme, I hear that's fun.",
    "Go bother someone else, no-one here cares.",
    "You can run, but you can't hide.",
    "Is that all you've got?",
    "I'm behind you...",
    "You've got company!",
    "We can do this the easy way, or the hard way.",
    "You just don't get it, do you?",
    "Yeah, you better run!",
    "Please, remind me how much I care?",
    "I'd run faster if I were you.",
    "That's definitely the droid we're looking for.",
    "May the odds be ever in your favour.",
    "Famous last words.",
    "And they disappeared forever, never to be seen again.",
    "\"Oh, look at me! I'm so cool, I can run from a bot!\" - this person",
    "Yeah yeah, just tap /kickme already.",
    "Here, take this ring and head to Mordor while you're at it.",
    "Legend has it, they're still running...",
    "Unlike Harry Potter, your parents can't protect you from me.",
    "Fear leads to anger. Anger leads to hate. Hate leads to suffering. "
    "If you keep running in fear, you might "
    "be the next Vader.",
    "Multiple calculations later, I have decided my interest in your shenanigans is exactly 0.",
    "Legend has it, they're still running.",
    "Keep it up, not sure we want you here anyway.",
    "You're a wiza- Oh. Wait. You're not Harry, keep moving.",
    "NO RUNNING IN THE HALLWAYS!",
    "Hasta la vista, baby.",
    "Who let the dogs out?",
    "It's funny, because no one cares.",
    "Ah, what a waste. I liked that one.",
    "Frankly, my dear, I don't give a damn.",
    "My milkshake brings all the boys to yard... So run faster!",
    "You can't HANDLE the truth!",
    "A long time ago, in a galaxy far far away... Someone would've cared about that. "
    "Not anymore though.",
    "Hey, look at them! They're running from the inevitable banhammer... Cute.",
    "Han shot first. So will I.",
    "What are you running after, a white rabbit?",
    "As The Doctor would say... RUN!")

INSULT_STRINGS = (
    "Owww ... Such a stupid idiot.",
    "Don't drink and type.",
    "I think you should go home or better a mental asylum.",
    "Command not found. Just like your brain.",
    "Do you realize you are making a fool of yourself? Apparently not.",
    "You can type better than that.",
    "Bot rule 544 section 9 prevents me from replying to stupid humans like you.",
    "Sorry, we do not sell brains.",
    "Believe me you are not normal.",
    "I bet your brain feels as good as new, seeing that you never use it.",
    "If I wanted to kill myself I'd climb your ego and jump to your IQ.",
    "Zombies eat brains... you're safe.",
    "You didn't evolve from apes, they evolved from you.",
    "Come back and talk to me when your I.Q. exceeds your age.",
    "I'm not saying you're stupid, I'm just saying you've got bad luck when it comes to thinking.",
    "What language are you speaking? Cause it sounds like bullshit.",
    "Stupidity is not a crime so you are free to go.",
    "You are proof that evolution CAN go in reverse.",
    "I would ask you how old you are but I know you can't count that high.",
    "As an outsider, what do you think of the human race?",
    "Brains aren't everything. In your case they're nothing.",
    "Ordinarily people live and learn. You just live.",
    "I don't know what makes you so stupid, but it really works.",
    "Keep talking, someday you'll say something intelligent! (I doubt it though)",
    "Shock me, say something intelligent.",
    "Your IQ's lower than your shoe size.",
    "Alas! Your neurotransmitters are no more working.",
    "Are you crazy you fool.",
    "Everyone has the right to be stupid but you are abusing the privilege.",
    "I'm sorry I hurt your feelings when I called you stupid. I thought you already knew that.",
    "You should try tasting cyanide.",
    "Your enzymes are meant to digest rat poison.",
    "You should try sleeping forever.",
    "Pick up a gun and shoot yourself.",
    "You could make a world record by jumping from a plane without parachute.",
    "Stop talking BS and jump in front of a running bullet train.",
    "Try bathing with Hydrochloric Acid instead of water.",
    "Try this: if you hold your breath underwater for an hour, you can then hold it forever.",
    "Go Green! Stop inhaling Oxygen.",
    "God was searching for you. You should leave to meet him.",
    "give your 100%. Now, go donate blood.",
    "Try jumping from a hundred story building but you can do it only once.",
    "You should donate your brain seeing that you never used it.",
    "Volunteer for target in an firing range.",
    "Head shots are fun. Get yourself one.",
    "You should try swimming with great white sharks.",
    "You should paint yourself red and run in a bull marathon.",
    "You can stay underwater for the rest of your life without coming back up.",
    "How about you stop breathing for like 1 day? That'll be great.",
    "Try provoking a tiger while you both are in a cage.",
    "Have you tried shooting yourself as high as 100m using a canon.",
    "You should try holding TNT in your mouth and igniting it.",
    "Try playing catch and throw with RDX its fun.",
    "I heard phogine is poisonous but i guess you wont mind inhaling it for fun.",
    "Launch yourself into outer space while forgetting oxygen on Earth.",
    "You should try playing snake and ladders, with real snakes and no ladders.",
    "Dance naked on a couple of HT wires.",
    "Active Volcano is the best swimming pool for you.",
    "You should try hot bath in a volcano.",
    "Try to spend one day in a coffin and it will be yours forever.",
    "Hit Uranium with a slow moving neutron in your presence. It will be a worthwhile experience.",
    "You can be the first person to step on sun. Have a try.")

EMOJIS = (
    "😂", "😂", "👌", "✌", "💞", "👍", "👌", "💯", "🎶", "👀", "😂", "👓", "👏", "👐", "🍕",
    "💥", "🍴", "💦", "💦", "🍑", "🍆", "😩", "😏", "👉👌", "👀", "👅", "😩", "🚰")

DICE_EMO = ("🎯", "🎲")

ZALG_LIST = (
    ("̖", " ̗", " ̘", " ̙", " ̜", " ̝", " ̞", " ̟", " ̠", " ̤", " ̥", " ̦", " ̩", " ̪", " ̫",
     " ̬", " ̭", " ̮", " ̯", " ̰", " ̱", " ̲", " ̳", " ̹", " ̺", " ̻", " ̼", " ͅ", " ͇",
     " ͈", " ͉", " ͍", " ͎", " ͓", " ͔", " ͕", " ͖", " ͙", " ͚", " "),

    (" ̍", " ̎", " ̄", " ̅", " ̿", " ̑", " ̆", " ̐", " ͒", " ͗", " ͑", " ̇", " ̈", " ̊",
     " ͂", " ̓", " ̈́", " ͊", " ͋", " ͌", " ̃", " ̂", " ̌", " ͐", " ́", " ̋", " ̏", " ̽",
     " ̉", " ͣ", " ͤ", " ͥ", " ͦ", " ͧ", " ͨ", " ͩ", " ͪ", " ͫ", " ͬ", " ͭ", " ͮ", " ͯ",
     " ̾", " ͛", " ͆", " ̚"),

    (" ̕", " ̛", " ̀", " ́", " ͘", " ̡", " ̢", " ̧", " ̨", " ̴", " ̵", " ̶", " ͜",
     " ͝", " ͞", " ͟", " ͠", " ͢", " ̸", " ̷", " ͡")
)

UWUS = (
    "(・`ω´・)", ";;w;;", "owo", "UwU", ">w<", "^w^", r"\(^o\) (/o^)/", "( ^ _ ^)∠☆", "(ô_ô)",
    "~:o", ";-;", "(*^*)", "(>_", "(♥_♥)", "*(^O^)*", "((+_+))")

SHGS = (
    "┐(´д｀)┌", "┐(´～｀)┌", "┐(´ー｀)┌", "┐(￣ヘ￣)┌", "╮(╯∀╰)╭", "╮(╯_╰)╭", "┐(´д`)┌", "┐(´∀｀)┌",
    "ʅ(́◡◝)ʃ", "┐(ﾟ～ﾟ)┌", "┐('д')┌", "┐(‘～`;)┌", "ヘ(´－｀;)ヘ", "┐( -“-)┌", "ʅ（´◔౪◔）ʃ",
    "ヽ(゜～゜o)ノ", "ヽ(~～~ )ノ", "┐(~ー~;)┌", "┐(-。ー;)┌", r"¯\_(ツ)_/¯", r"¯\_(⊙_ʖ⊙)_/¯",
    r"¯\_༼ ಥ ‿ ಥ ༽_/¯", "乁( ⁰͡  Ĺ̯ ⁰͡ ) ㄏ")

CRI = (
    "أ‿أ", "╥﹏╥", "(;﹏;)", "(ToT)", "(┳Д┳)", "(ಥ﹏ಥ)", "（；へ：）", "(T＿T)", "（πーπ）", "(Ｔ▽Ｔ)",
    "(⋟﹏⋞)", "（ｉДｉ）", "(´Д⊂ヽ", "(;Д;)", "（>﹏<）", "(TдT)", "(つ﹏⊂)", "༼☯﹏☯༽", "(ノ﹏ヽ)",
    "(ノAヽ)", "(╥_╥)", "(T⌓T)", "(༎ຶ⌑༎ຶ)", "(☍﹏⁰)｡", "(ಥ_ʖಥ)", "(つд⊂)", "(≖͞_≖̥)", "(இ﹏இ`｡)",
    "༼ಢ_ಢ༽", "༼ ༎ຶ ෴ ༎ຶ༽")

FACEREACTS = (
    "ʘ‿ʘ", "ヾ(-_- )ゞ", "(っ˘ڡ˘ς)", "(´ж｀ς)", "( ಠ ʖ̯ ಠ)", "(° ͜ʖ͡°)╭∩╮", "(ᵟຶ︵ ᵟຶ)", "(งツ)ว",
    "ʚ(•｀", "(っ▀¯▀)つ", "(◠﹏◠)", "( ͡ಠ ʖ̯ ͡ಠ)", "( ఠ ͟ʖ ఠ)", "(∩｀-´)⊃━☆ﾟ.*･｡ﾟ", "(⊃｡•́‿•̀｡)⊃",
    "(._.)", "{•̃_•̃}", "(ᵔᴥᵔ)", "♨_♨", "⥀.⥀", "ح˚௰˚づ ", "(҂◡_◡)", "ƪ(ړײ)‎ƪ​​", "(っ•́｡•́)♪♬",
    "◖ᵔᴥᵔ◗ ♪ ♫ ", "(☞ﾟヮﾟ)☞", "[¬º-°]¬", "(Ծ‸ Ծ)", "(•̀ᴗ•́)و ̑̑", "ヾ(´〇`)ﾉ♪♪♪", "(ง'̀-'́)ง",
    "ლ(•́•́ლ)", "ʕ •́؈•̀ ₎", "♪♪ ヽ(ˇ∀ˇ )ゞ", "щ（ﾟДﾟщ）", "( ˇ෴ˇ )", "눈_눈", "(๑•́ ₃ •̀๑) ",
    "( ˘ ³˘)♥ ", "ԅ(≖‿≖ԅ)", "♥‿♥", "◔_◔", "⁽⁽ଘ( ˊᵕˋ )ଓ⁾⁾", "乁( ◔ ౪◔)「      ┑(￣Д ￣)┍",
    "( ఠൠఠ )ﾉ", "٩(๏_๏)۶", "┌(ㆆ㉨ㆆ)ʃ", "ఠ_ఠ", "(づ｡◕‿‿◕｡)づ", "༼ ༎ຶ ෴ ༎ຶ༽", "｡ﾟ( ﾟஇ‸இﾟ)ﾟ｡",
    "(づ￣ ³￣)づ", "(⊙.☉)7", "ᕕ( ᐛ )ᕗ", "t(-_-t)", "(ಥ⌣ಥ)", "ヽ༼ ಠ益ಠ ༽ﾉ", "༼∵༽ ༼⍨༽ ༼⍢༽ ༼⍤༽",
    "ミ●﹏☉ミ", "(⊙_◎)", "¿ⓧ_ⓧﮌ", "ಠ_ಠ", "(´･_･`)", "ᕦ(ò_óˇ)ᕤ", "⊙﹏⊙", "(╯°□°）╯︵ ┻━┻",
    r"¯\_(⊙︿⊙)_/¯", "٩◔̯◔۶", "°‿‿°", "ᕙ(⇀‸↼‶)ᕗ", "⊂(◉‿◉)つ", "V•ᴥ•V", "q(❂‿❂)p", "ಥ_ಥ",
    "ฅ^•ﻌ•^ฅ", "ಥ﹏ಥ", "（ ^_^）o自自o（^_^ ）", "ಠ‿ಠ", "ヽ(´▽`)/", "ᵒᴥᵒ#", "( ͡° ͜ʖ ͡°)",
    "┬─┬﻿ ノ( ゜-゜ノ)", "ヽ(´ー｀)ノ", "☜(⌒▽⌒)☞", "ε=ε=ε=┌(;*´Д`)ﾉ", "(╬ ಠ益ಠ)", "┬─┬⃰͡ (ᵔᵕᵔ͜ )",
    "┻━┻ ︵ヽ(`Д´)ﾉ︵﻿ ┻━┻", r"¯\_(ツ)_/¯", "ʕᵔᴥᵔʔ", "(`･ω･´)", "ʕ•ᴥ•ʔ", "ლ(｀ー´ლ)", "ʕʘ̅͜ʘ̅ʔ",
    "（　ﾟДﾟ）", r"¯\(°_o)/¯", "(｡◕‿◕｡)", "(ノಠ ∩ಠ)ノ彡( \\o°o)\\", "“ヽ(´▽｀)ノ”", "( ͡° ͜ʖ ͡°)",
    r"¯\_(ツ)_/¯", "( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)", "ʕ•ᴥ•ʔ", "(▀̿Ĺ̯▀̿ ̿)", "(ง ͠° ͟ل͜ ͡°)ง",
    "༼ つ ◕_◕ ༽つ", "ಠ_ಠ", "(☞ ͡° ͜ʖ ͡°)☞", "¯_༼ ି ~ ି ༽_/¯", "c༼ ͡° ͜ʖ ͡° ༽⊃")

HAPPY = ("( ͡° ͜ʖ ͡°)", "(ʘ‿ʘ)", "(✿´‿`)", "=͟͟͞͞٩(๑☉ᴗ☉)੭ु⁾⁾", "(*⌒▽⌒*)θ～♪",
         "°˖✧◝(⁰▿⁰)◜✧˖°", "✌(-‿-)✌", "⌒°(❛ᴗ❛)°⌒", "(ﾟ<|＼(･ω･)／|>ﾟ)", "ヾ(o✪‿✪o)ｼ")

THINKING = ("(҂⌣̀_⌣́)", "（；¬＿¬)", "(-｡-;", "┌[ O ʖ̯ O ]┐", "〳 ͡° Ĺ̯ ͡° 〵")

WAVING = (
    "(ノ^∇^)", "(;-_-)/", "@(o・ェ・)@ノ", "ヾ(＾-＾)ノ", "ヾ(◍’౪`◍)ﾉﾞ♡", "(ό‿ὸ)ﾉ", "(ヾ(´・ω・｀)")

WTF = ("༎ຶ‿༎ຶ", "(‿ˠ‿)", "╰U╯☜(◉ɷ◉ )", "(;´༎ຶ益༎ຶ`)♡", "╭∩╮(︶ε︶*)chu", "( ＾◡＾)っ (‿|‿)")

LOVE = ("乂❤‿❤乂", "(｡♥‿♥｡)", "( ͡~ ͜ʖ ͡°)", "໒( ♥ ◡ ♥ )७", "༼♥ل͜♥༽")

CONFUSED = ("(・_・ヾ", "｢(ﾟﾍﾟ)", "﴾͡๏̯͡๏﴿", "(￣■￣;)!?", "▐ ˵ ͠° (oo) °͠ ˵ ▐", "(-_-)ゞ゛")

DEAD = ("(✖╭╮✖)", "✖‿✖", "(+_+)", "(✖﹏✖)", "∑(✘Д✘๑)")

SAD = ("(＠´＿｀＠)", "⊙︿⊙", "(▰˘︹˘▰)", "●︿●", "(　´_ﾉ` )", "彡(-_-;)彡")

DOG = ("-ᄒᴥᄒ-", "◖⚆ᴥ⚆◗")
