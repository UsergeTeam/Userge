""" generate direct link of zippyshare """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

# !/usr/bin/env python3
# https://github.com/Sorrow446/ZS-DL
# plugin by @aryanvikash

import re

import requests

from userge import userge, Message, pool


@userge.on_cmd("zippy", about={
    'header': "generate Direct link of zippyshare url",
    'usage': "{tr}zippy : [Zippyshare Link ]",
    'examples': "{tr}zippy https://www10.zippyshare.com/v/dyh988sh/file.html"})
async def zippyshare(message: Message):
    """ zippy to direct """
    url = message.input_str
    await message.edit("`Generating url ....`")
    try:
        direct_url, fname = await _generate_zippylink(url)
        await message.edit(f"**Original** : {url}\n**FileName** : `{fname}`\n"
                           f"**DirectLink** : {direct_url}\n\n"
                           "**[HINT]** : use `.download [directLink]`",
                           disable_web_page_preview=True)
    except Exception as z_e:  # pylint: disable=broad-except
        await message.edit(f"`{z_e}`")


_REGEX_LINK = r'https://www(\d{1,3}).zippyshare.com/v/(\w{8})/file.html'
_REGEX_RESULT = (
    r'document.getElementById\(\'dlbutton\'\).href = "/d/[a-zA-Z\d]{8}/" \+ '
    r'\((\d{6}) % 51245 \+ (\d{6}) % 913\) \+ "/([\w%-.]+)";'
)
_HEADERS = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
                          "/75.0.3770.100 Safari/537.36"}


@pool.run_in_thread
def _generate_zippylink(url):
    session = requests.Session()
    session.headers.update(_HEADERS)
    with session as ses:
        match = re.match(_REGEX_LINK, url)
        if not match:
            raise ValueError("Invalid URL: " + str(url))
        server, id_ = match.group(1), match.group(2)
        res = ses.get(url)
        res.raise_for_status()
        match = re.search(_REGEX_RESULT, res.text, re.DOTALL)
        if not match:
            raise ValueError("Invalid Response!")
        val_1 = int(match.group(1))
        val_2 = int(match.group(2))
        val = val_1 % 51245 + val_2 % 913
        name = match.group(3)
        d_l = "https://www{}.zippyshare.com/d/{}/{}/{}".format(server, id_, val, name)
    return d_l, name
