""" parse gdtot and appdrive links """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

# Plugin By @ZekXtreme
# Base Script by <https://github.com/xcscxr>

import base64
import json
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from userge import Message, userge, pool
from .. import parser


@userge.on_start
async def _init():
    if parser.Dynamic.CRYPT:
        try:
            crypt = json.loads(parser.Dynamic.CRYPT)
        except Exception:
            pass  # user entered only crypt value from dict
        else:
            parser.Dynamic.CRYPT = crypt.get("cookie").split('=')[-1]


async def account_login(client, url):
    data = {
        'email': parser.APPDRIVE_EMAIL,
        'password': parser.APPDRIVE_PASS
    }
    await pool.run_in_thread(client.post)(
        f'https://{urlparse(url).netloc}/login', data=data)


def gen_payload(data, boundary=f'{"-"*6}_'):
    data_string = ''
    for item in data:
        data_string += f'{boundary}\r\n'
        data_string += f'Content-Disposition: form-data; name="{item}"\r\n\r\n{data[item]}\r\n'
    data_string += f'{boundary}--\r\n'
    return data_string


def parse_info(data):
    soup = BeautifulSoup(data, 'html.parser')
    info = soup.find_all('li', {'class': 'list-group-item'})
    info_parsed = {}
    for item in info:
        kv = [s.strip() for s in item.text.split(':', maxsplit=1)]
        info_parsed[kv[0].lower()] = kv[1]
    return info_parsed


async def appdrive_dl(url):
    client = requests.Session()
    client.headers.update({
        "user-agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/97.0.4692.99 Safari/537.36")
    })
    await account_login(client, url)
    res = await pool.run_in_thread(client.get)(url)
    key = re.findall(r'"key",\s+"(.*?)"', res.text)[0]
    soup = BeautifulSoup(res.content, 'html.parser')
    ddl_btn = soup.find('button', {'id': 'drc'})
    info_parsed = parse_info(res.text)
    info_parsed['error'] = False
    info_parsed['link_type'] = 'login'  # direct/login
    headers = {
        "Content-Type": f"multipart/form-data; boundary={'-'*4}_",
    }

    data = {
        'key': key,
        'action': 'original',
        'type': 1
    }

    if ddl_btn:
        data['action'] = 'direct'
        info_parsed['link_type'] = 'direct'

    while data['type'] <= 3:
        try:
            response = (await pool.run_in_thread(client.post)(
                url,
                data=gen_payload(data),
                headers=headers
            )).json()
            break
        except Exception as e:
            if data['type'] == 3:
                response = {
                    'error': True,
                    'message': str(e)
                }
            data['type'] += 1

    if 'url' in response:
        info_parsed['gdrive_link'] = response['url']
    else:
        info_parsed['error'] = True
        info_parsed['error_message'] = response.get('message', 'Something went wrong :(')
    return info_parsed


@userge.on_cmd("gdtot", about={
    'header': "parse gdtot links",
    'description': "you have to set <code>CRYPT</code>.\nget it by reading "
                   "<a href='https://t.me/UsergePlugins/129'>Help</a>",
    'usage': "{tr}gdtot gdtot_link"})
async def gdtot(message: Message):
    """ Gets gdrive link """
    if not parser.Dynamic.CRYPT:
        return await message.err("read .help gdtot")
    client = requests.Session()
    client.cookies.update({'crypt': parser.Dynamic.CRYPT})
    args = message.input_str
    if not args:
        await message.err("Send a link along with command")
    else:
        try:
            await message.edit("Parsing...")
            res = await pool.run_in_thread(client.get)(args)
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.find(
                'h5', {'class': lambda x: x and "modal-title" not in x}).text
            info = soup.find_all('td', {'align': 'right'})
            res = await pool.run_in_thread(client.get)(
                f"https://new.gdtot.top/dld?id={args.split('/')[-1]}")
            matches = re.findall(r'gd=(.*?)&', res.text)
            decoded_id = base64.b64decode(str(matches[0])).decode('utf-8')
            gdrive_url = f'https://drive.google.com/open?id={decoded_id}'
            out = (
                f'Title: {title.strip()}\n'
                f'Size: {info[0].text.strip()}\n'
                f'Date: {info[1].text.strip()}\n'
                f'\nGDrive-URL:\n{gdrive_url}'
            )
            await message.edit(out, disable_web_page_preview=True)
        except Exception:
            await message.err("Unable To parse Link")


@userge.on_cmd("appdrive", about={
    'header': "parse appdrive links",
    'description': "you have to set <code>Required Vars</code>.\nget it by reading "
                   "<a href='https://t.me/UsergePlugins/129'>Help</a>",
    'usage': "{tr}appdrive appdrive_link"})
async def appdrive(message: Message):
    if not (parser.APPDRIVE_EMAIL or parser.APPDRIVE_PASS):
        return await message.err("read .help appdrive")
    url = message.input_str
    if not url:
        await message.err("Send a link along with command")
    else:
        await message.edit("Parsing.....")
        res = await appdrive_dl(url)
        if res.get('error') and res.get('error_message'):
            await message.err(res.get('error_message'))
        else:
            output = (
                f'Title: {res.get("name")}\n'
                f'Format: {res.get("format")}\n'
                f'Size: {res.get("size")}\n'
                'Drive_Link: '
                f'{res.get("gdrive_link", "Something Went Wrong")}'
            )
            await message.edit(output, disable_web_page_preview=True)
