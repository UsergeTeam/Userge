import os

import urllib

import requests

import asyncio

from asyncio import sleep

from userge import userge , Message, Config

@userge.on_cmd("boobs", about={

    'header': "Find some Bob",

    'usage': "{tr}boobs"})

async def boobs(message: Message):

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
