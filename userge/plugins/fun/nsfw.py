import os

import urllib

import requests

import asyncio

from userge import userge , Message, Config

from pyrogram.types import CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

from pyrogram import filters

from userge.utils import get_file_id_and_ref

from pyrogram.errors import MessageNotModified

 

async def age_verification(msg):

    if Config.ALLOW_NSFW.lower() == "true":

        return False

    bot = await userge.bot.get_me()

    x = await userge.get_inline_bot_results(bot.username, "age_verification_alert")

    await msg.delete()

    await userge.send_inline_bot_result(

        chat_id=msg.chat.id,

        query_id=x.query_id,

        result_id=x.results[0].id

    )

    return True

@userge.on_cmd("boobs", about={

    'header': "Find some Bob",

    'usage': "{tr}boobs"})

async def boobs(message: Message):

    if await age_verification(message):

        return

    if not os.path.isdir(Config.DOWN_PATH):

        os.makedirs(Config.DOWN_PATH)

    pic_loc = os.path.join(Config.DOWN_PATH, "bobs.jpg")

    await message.edit("`Finding some big bobs 🧐...`")

    await asyncio.sleep(0.5)

    await message.edit("`Sending some big bobs 🌚...`")

    nsfw = requests.get('http://api.oboobs.ru/noise/1').json()[0]["preview"]

    urllib.request.urlretrieve("http://media.oboobs.ru/{}".format(nsfw), pic_loc)

    await message.client.send_photo(message.chat.id, photo=pic_loc)

    os.remove(pic_loc)

    await message.delete()

@userge.on_cmd("butts", about={

    'header': "Find some Butts",

    'usage': "{tr}butts"})

async def butts(message: Message):

    if await age_verification(message):

        return

    if not os.path.isdir(Config.DOWN_PATH):

        os.makedirs(Config.DOWN_PATH)

    pic_loc = os.path.join(Config.DOWN_PATH, "bobs.jpg")

    await message.edit("`Finding some beautiful butts 🧐...`")

    await asyncio.sleep(0.5)

    await message.edit("`Sending some beautiful butts 🌚...`")

    nsfw = requests.get('http://api.obutts.ru/noise/1').json()[0]["preview"]

    urllib.request.urlretrieve("http://media.obutts.ru/{}".format(nsfw), pic_loc)

    await message.client.send_photo(message.chat.id, photo=pic_loc)

    os.remove(pic_loc)

    await message.delete()

if Config.BOT_TOKEN and Config.OWNER_ID:

    if Config.HU_STRING_SESSION:

        ubot = userge.bot

    else:

        ubot = userge

       

    @ubot.on_callback_query(filters.regex(pattern=r"^age_verification_true"))

    async def alive_callback(_, c_q: CallbackQuery):

        u_id = c_q.from_user.id

        if u_id != Config.OWNER_ID and u_id not in Config.SUDO_USERS:

            return await c_q.answer("Given That It\'s A Stupid-Ass Decision, I\'ve Elected To Ignore It.", show_alert=True)

        await c_q.answer("Yes I\'m 18+", show_alert=False)

        msg = await ubot.get_messages('useless_x' , 19)

        f_id, f_ref = get_file_id_and_ref(msg)

        buttons = [[

            InlineKeyboardButton(

            text="Unsure / Change of Decision ❔", 

            callback_data="chg_of_decision_"

            )

        ]]

        try:

            await c_q.edit_message_media(

                media=InputMediaPhoto(

                            media=f_id,

                            file_ref=f_ref,

                            caption="Set <code>ALLOW_NSFW</code> = True in Heroku Vars to access this plugin"

                        ),

                reply_markup=InlineKeyboardMarkup(buttons)

            )

        except MessageNotModified:

            return

    @ubot.on_callback_query(filters.regex(pattern=r"^age_verification_false"))

    async def alive_callback(_, c_q: CallbackQuery):

        u_id = c_q.from_user.id

        if u_id != Config.OWNER_ID and u_id not in Config.SUDO_USERS:

            return await c_q.answer("Given That It\'s A Stupid-Ass Decision, I\'ve Elected To Ignore It.", show_alert=True)

        await c_q.answer("No I'm Not", show_alert=False)

        msg = await ubot.get_messages('useless_x' , 20)

        f_id, f_ref = get_file_id_and_ref(msg)

        img_text="GO AWAY KID !"

        buttons = [[

            InlineKeyboardButton(

            text="Unsure / Change of Decision ❔", 

            callback_data="chg_of_decision_"

            )

        ]]

        try:

            await c_q.edit_message_media(

                media=InputMediaPhoto(

                            media=f_id,

                            file_ref=f_ref,

                            caption=img_text

                        ),

                reply_markup=InlineKeyboardMarkup(buttons)

            )

        except MessageNotModified:

            return

        

    @ubot.on_callback_query(filters.regex(pattern=r"^chg_of_decision_"))

    async def alive_callback(_, c_q: CallbackQuery):

        u_id = c_q.from_user.id

        if u_id != Config.OWNER_ID and u_id not in Config.SUDO_USERS:

            return await c_q.answer("Given That It\'s A Stupid-Ass Decision, I\'ve Elected To Ignore It.", show_alert=True)

        await c_q.answer("Unsure", show_alert=False)

        msg = await ubot.get_messages('useless_x', 21)

        f_id, f_ref = get_file_id_and_ref(msg)

        img_text="**ARE YOU OLD ENOUGH FOR THIS ?**"

        buttons = [[

                        InlineKeyboardButton(

                        text="Yes I'm 18+", 

                        callback_data="age_verification_true"

                        ),

                        InlineKeyboardButton(

                        text="No I'm Not", 

                        callback_data="age_verification_false"

                        )

                ]]

        try:

            await c_q.edit_message_media(

                media=InputMediaPhoto(

                            media=f_id,

                            file_ref=f_ref,

                            caption=img_text

                        ),

                reply_markup=InlineKeyboardMarkup(buttons)

            )

        except MessageNotModified:

            return
