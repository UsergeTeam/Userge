""" paste text to bin """

# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import re
from typing import Optional, Dict

import aiohttp
import aiofiles

from userge import userge, Message, Config


class PasteService:
    def __init__(self, name: str, url: str) -> None:
        self._name = name
        self._url = url.rstrip('/') + '/'

    def get_name(self) -> str:
        """ returns service name """
        return self._name

    def is_supported(self, url: str) -> bool:
        """ returns True if url supports service """
        if url.startswith((self._url, self._url.replace("https://", ""))):
            return True
        return False

    # pylint: disable=W0613
    async def paste(self, ses: aiohttp.ClientSession,
                    text: str, file_type: Optional[str]) -> Optional[str]:
        """ returns the success url or None if failed """
        return None

    async def get_paste(self, ses: aiohttp.ClientSession, code: str) -> Optional[str]:
        """ returns pasted text using this code or None if failed """
        async with ses.get(self._url + "raw/" + code) as resp:
            if resp.status == 404:
                async with ses.get(self._url + code + "/raw") as _resp:
                    if _resp.status != 200:
                        return None
                    return await _resp.text()
            if resp.status != 200:
                return None
            return await resp.text()


class NekoBin(PasteService):
    def __init__(self) -> None:
        super().__init__("nekobin", "https://nekobin.com/")

    async def paste(self, ses: aiohttp.ClientSession,
                    text: str, file_type: Optional[str]) -> Optional[str]:
        async with ses.post(self._url + "api/documents", json={"content": text}) as resp:
            if resp.status != 201:
                return None
            response = await resp.json()
            key = response['result']['key']
            final_url = self._url + key
            if file_type:
                final_url += "." + file_type
            return final_url

    async def get_paste(self, ses: aiohttp.ClientSession, code: str) -> Optional[str]:
        async with ses.get(self._url + "api/documents/" + code) as resp:
            if resp.status != 200:
                return None
            response = await resp.json()
            return response['result']['content']


class HasteBin(PasteService):
    def __init__(self) -> None:
        super().__init__("hastebin", "https://hastebin.com/")

    async def paste(self, ses: aiohttp.ClientSession,
                    text: str, file_type: Optional[str]) -> Optional[str]:
        async with ses.post(self._url + "documents", data=text) as resp:
            if resp.status != 200:
                return None
            response = await resp.json()
            key = response['key']
            final_url = self._url + key
            if file_type:
                final_url += "." + file_type
            return final_url


class Rentry(PasteService):
    def __init__(self) -> None:
        super().__init__("rentry", "https://rentry.co/")

    async def paste(self, ses: aiohttp.ClientSession,
                    text: str, file_type: Optional[str]) -> Optional[str]:
        token = None
        async with ses.get(self._url) as resp:
            if resp.status != 200:
                return None
            content = await resp.text()
            for i in re.finditer(r'name="csrfmiddlewaretoken" value="(.+)"', content):
                token = i.group(1)
                break
            if not token:
                return None
        if file_type:
            text = f"```{file_type}\n" + text + "\n```"
        async with ses.post(self._url,
                            data=dict(csrfmiddlewaretoken=token, text=text),
                            headers=dict(Referer=self._url),
                            allow_redirects=True) as resp:
            if resp.status != 200:
                return None
            return str(resp.url)


class Pasting(PasteService):
    def __init__(self) -> None:
        super().__init__("pasting", "https://pasting.ga/")

    async def paste(self, ses: aiohttp.ClientSession,
                    text: str, file_type: Optional[str]) -> Optional[str]:
        data = {"content": text}
        if file_type:
            data['code'] = "true"
        async with ses.post(self._url + "api", json=data) as resp:
            if resp.status != 200:
                return None
            code = await resp.text()
            return self._url + code


class PastyLus(PasteService):
    def __init__(self) -> None:
        super().__init__("pasty.lus", "https://pasty.lus.pm/")

    async def paste(self, ses: aiohttp.ClientSession,
                    text: str, file_type: Optional[str]) -> Optional[str]:
        async with ses.post(self._url + "api/v2/pastes/", json={"content": text}) as resp:
            if resp.status != 201:
                return None
            content = await resp.text()
            code = ""
            for i in re.finditer(r'"id":"(.+?)"', content):
                code = i.group(1)
                break
            if not code:
                return None
            final_url = self._url + code
            if file_type:
                final_url += '.' + file_type
            return final_url


class Katbin(PasteService):
    def __init__(self) -> None:
        self._api_url = "https://api.katb.in/api/paste/"
        super().__init__("katbin", "https://katb.in/")

    async def paste(self, ses: aiohttp.ClientSession,
                    text: str, file_type: Optional[str]) -> Optional[str]:
        async with ses.post(self._api_url, json={"content": text}) as resp:
            if resp.status != 201:
                return None
            response = await resp.json()
            key = response['paste_id']
            final_url = self._url + key
            if file_type:
                final_url += "." + file_type
            return final_url

    async def get_paste(self, ses: aiohttp.ClientSession, code: str) -> Optional[str]:
        async with ses.get(self._api_url + code) as resp:
            if resp.status != 200:
                return None
            response = await resp.json()
            return response['content']


_SERVICES: Dict[str, PasteService] = {
    '-n': NekoBin(), '-h': HasteBin(), '-r': Rentry(),
    '-p': Pasting(), '-pl': PastyLus(), '-k': Katbin()}

if Config.HEROKU_ENV:
    _DEFAULT_SERVICE = '-pl'
else:
    _DEFAULT_SERVICE = '-n'

_HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 ('
                          'KHTML, like Gecko) Cafari/537.36'}


def _get_code(url: str) -> Optional[str]:
    parts = list(filter(None, url.split('/')))
    if len(parts) < 2:
        return None
    code = parts.pop(-1)
    if code.lower() == "raw":
        code = parts.pop(-1)
    return code.split('.')[0]


@userge.on_cmd("paste", about={
    'header': "Pastes text or text_file to a bin service",
    'flags': {k: f"use {v.get_name()}" for k, v in _SERVICES.items()},
    'usage': "{tr}paste [flags] [file_type] [text | reply to msg]",
    'examples': "{tr}paste -py import os"})
async def paste_(message: Message) -> None:
    """ pastes the text directly to a bin service """
    await message.edit("`Processing...`")
    text = message.filtered_input_str
    replied = message.reply_to_message
    file_type = None
    if not text and replied and replied.document and replied.document.file_size < 2 ** 20 * 10:
        file_type = os.path.splitext(replied.document.file_name)[1].lstrip('.')
        path = await replied.download(Config.DOWN_PATH)
        async with aiofiles.open(path, 'r') as d_f:
            text = await d_f.read()
        os.remove(path)
    elif not text and replied and replied.text:
        text = replied.text
    if not text:
        await message.err("input not found!")
        return
    flags = list(message.flags)
    size = len(flags)
    if size > 2:
        await message.err("too many args!")
        return

    service: Optional[PasteService] = None
    if size == 2:
        service = _SERVICES.get(flags[0])
        file_type = flags[1].lstrip('-')
    elif size == 1:
        service = _SERVICES.get(flags[0])
        if not service:
            file_type = flags[0].lstrip('-')
    if not service:
        service = _SERVICES[_DEFAULT_SERVICE]

    await message.edit(f"`Pasting text to [{service.get_name().title()}] ...`")
    async with aiohttp.ClientSession(headers=_HEADERS) as ses:
        url = await service.paste(ses, text, file_type)
        if url is None:
            await message.edit(f"`Failed to reach {service.get_name().title()}`", del_in=5)
        else:
            await message.edit(f"**{service.get_name().title()}** [URL]({url})",
                               disable_web_page_preview=True)


@userge.on_cmd("getpaste", about={
    'header': "Gets the content of a paste url",
    'types': [s.get_name() for s in _SERVICES.values()],
    'usage': "{tr}getpaste [paste link]"})
async def get_paste_(message: Message):
    """ fetches the content of a paste URL """
    link = message.input_str
    if not link:
        await message.err("input not found!")
        return
    await message.edit("`Finding Service...`")

    for service in _SERVICES.values():
        if service.is_supported(link):
            code = _get_code(link)
            if code is None:
                await message.err("Invalid Link !")
                return
            await message.edit(f"`Getting paste content [{service.get_name().title()}] ...`")
            async with aiohttp.ClientSession(headers=_HEADERS) as ses:
                text = await service.get_paste(ses, code)
                if text is None:
                    await message.edit(f"`Failed to reach {service.get_name().title()}`", del_in=5)
                else:
                    await message.edit_or_send_as_file(f"**Content** :\n`{text}`")
            return

    await message.err("Is that even a paste url?")
