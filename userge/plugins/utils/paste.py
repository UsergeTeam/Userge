""" paste text to bin """

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
NEKOBIN_URL = "https://nekobin.com/"


@userge.on_cmd("paste", about={
    'header': "Pastes text or text_file to dogbin",
    'flags': {'-n': "use nekobin"},
    'usage': "{tr}paste [flags] [file_type] [text | reply to msg]",
    'examples': "{tr}paste -py import os"}, del_pre=True)
async def paste_(message: Message) -> None:
    """ pastes the text directly to dogbin or nekobin """
    await message.edit("`Processing...`")
    text = message.filtered_input_str
    replied = message.reply_to_message
    use_neko = False
    file_ext = '.txt'
    if not text and replied and replied.document and replied.document.file_size < 2 ** 20 * 10:
        file_ext = os.path.splitext(replied.document.file_name)[1]
        path = await replied.download(Config.DOWN_PATH)
        with open(path, 'r') as d_f:
            text = d_f.read()
        os.remove(path)
    elif not text and replied and replied.text:
        text = replied.text
    if not text:
        await message.err("input not found!")
        return
    flags = list(message.flags)
    if 'n' in flags:
        use_neko = True
        flags.remove('n')
    if flags and len(flags) == 1:
        file_ext = '.' + flags[0]
    await message.edit("`Pasting text ...`")
    if use_neko:
        resp = post(NEKOBIN_URL + "api/documents", json={"content": text})
        if resp.status_code == 201:
            response = resp.json()
            key = response['result']['key']
            final_url = NEKOBIN_URL + key + file_ext
            reply_text = f"**Nekobin** [URL]({final_url})"
            await message.edit(reply_text, disable_web_page_preview=True)
        else:
            await message.err("Failed to reach Nekobin")
    else:
        resp = post(DOGBIN_URL + "documents", data=text.encode('utf-8'))
        if resp.status_code == 200:
            response = resp.json()
            key = response['key']
            final_url = DOGBIN_URL + key
            if response['isUrl']:
                reply_text = (f"**Shortened** [URL]({final_url})\n"
                              f"**Dogbin** [URL]({DOGBIN_URL}v/{key})")
            else:
                reply_text = f"**Dogbin** [URL]({final_url}{file_ext})"
            await message.edit(reply_text, disable_web_page_preview=True)
        else:
            await message.err("Failed to reach Dogbin")


@userge.on_cmd("getpaste", about={
    'header': "Gets the content of a del.dog paste",
    'usage': "{tr}getpaste [del.dog or nekobin link]"})
async def get_paste_(message: Message):
    """ fetches the content of a dogbin or nekobin URL """
    link = message.input_str
    if not link:
        await message.err("input not found!")
        return
    await message.edit("`Getting paste content...`")
    format_view = f'{DOGBIN_URL}v/'
    if link.startswith(format_view):
        link = link[len(format_view):]
        raw_link = f'{DOGBIN_URL}raw/{link}'
    elif link.startswith(DOGBIN_URL):
        link = link[len(DOGBIN_URL):]
        raw_link = f'{DOGBIN_URL}raw/{link}'
    elif link.startswith("del.dog/"):
        link = link[len("del.dog/"):]
        raw_link = f'{DOGBIN_URL}raw/{link}'
    elif link.startswith(NEKOBIN_URL):
        link = link[len(NEKOBIN_URL):]
        raw_link = f'{NEKOBIN_URL}raw/{link}'
    elif link.startswith("nekobin.com/"):
        link = link[len("nekobin.com/"):]
        raw_link = f'{NEKOBIN_URL}raw/{link}'
    else:
        await message.err("Is that even a paste url?")
        return
    resp = get(raw_link)
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
        await message.edit_or_send_as_file(
            f"--Fetched dogbin URL content successfully!--\n\n**Content** :\n`{resp.text}`")
