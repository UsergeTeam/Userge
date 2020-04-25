# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import os
from requests import get, post
from requests.exceptions import HTTPError, Timeout, TooManyRedirects

from userge import userge, Message, Config


DOGBIN_URL = "https://del.dog/"


@userge.on_cmd("paste", about={
    'header': "Pastes text or text_file to dogbin",
    'usage': ".paste [text | reply to msg]"})
async def paste_(message: Message):
    """pastes the text directly to dogbin"""

    await message.edit("`Processing...`")

    text = message.input_str
    replied = message.reply_to_message

    if not text and replied and replied.document and replied.document.file_size < 2 ** 20 * 10:
        path = await replied.download(Config.DOWN_PATH)

        with open(path, 'r') as d_f:
            text = d_f.read()

        os.remove(path)

    elif not text and replied and replied.text:
        text = replied.text

    if not text:
        await message.err("input not found!")
        return

    await message.edit("`Pasting text . . .`")

    resp = post(DOGBIN_URL + "documents", data=text.encode('utf-8'))

    if resp.status_code == 200:
        response = resp.json()
        key = response['key']
        dogbin_final_url = DOGBIN_URL + key

        reply_text = "--Pasted successfully!--\n\n"

        if response['isUrl']:
            reply_text += (f"**Shortened URL** : {dogbin_final_url}\n"
                           f"**Dogbin URL** : {DOGBIN_URL}v/{key}")

        else:
            reply_text += f"**Dogbin URL** : {dogbin_final_url}"

        await message.edit(reply_text)

    else:
        await message.err("Failed to reach Dogbin")


@userge.on_cmd("getpaste", about={
    'header': "Gets the content of a del.dog paste",
    'usage': ".getpaste [del.dog link]"})
async def get_paste_(message: Message):
    """fetches the content of a dogbin URL"""

    link = message.input_str

    if not link:
        await message.err("input not found!")
        return

    await message.edit("`Getting dogbin content...`")

    format_view = f'{DOGBIN_URL}v/'

    if link.startswith(format_view):
        link = link[len(format_view):]

    elif link.startswith(DOGBIN_URL):
        link = link[len(DOGBIN_URL):]

    elif link.startswith("del.dog/"):
        link = link[len("del.dog/"):]

    else:
        await message.err("Is that even a dogbin url?")
        return

    resp = get(f'{DOGBIN_URL}raw/{link}')

    try:
        resp.raise_for_status()

    except HTTPError:
        await message.err(
            f"Request returned an unsuccessful status code -> {HTTPError}")

    except Timeout:
        await message.err(f"Request timed out -> {Timeout}")

    except TooManyRedirects:
        await message.err(
            f"Request exceeded the configured number of maximum redirections -> {TooManyRedirects}")

    else:
        await message.edit(
            f"--Fetched dogbin URL content successfully!--\n\n**Content** :\n`{resp.text}`")
