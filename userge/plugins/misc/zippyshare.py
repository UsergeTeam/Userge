#!/usr/bin/env python3
# https://github.com/Sorrow446/ZS-DL
# plugin by @aryanvikash

import re
# import json
import time
try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

import requests

from userge import userge, Message, pool


@userge.on_cmd("dropg", about={
    'header': "generate Direct link of dropg url",
    'usage': "{tr}dropg : [Dropgalaxy Link ]",
    'examples': "{tr}drop https://dropgalaxy.in/lqox9et1uq5v/file.html"}, del_pre=True)
async def dropgalaxy(message: Message):
    """ dropg to direct """
    url = message.input_str
    await message.edit("`Generating url ....`")
    try:
        direct_url, fname = await _generate_dropglink(url)
        await message.edit(
            f"Original : {url}\n\nFilename : `{fname}`\n\nDirect link : {direct_url}")
    except Exception as z_e:  # pylint: disable=broad-except
        await message.edit(f"`{z_e}`")


# From Here script part starts

# def _decrypt_dlc(abs):
#     # Thank you, dcrypt owner(s).
#     url = "http://dcrypt.it/decrypt/paste"
#     r = s.post(url, data={
#         'content': open(abs)
#     }
#     )
#     r.raise_for_status()
#     j = json.loads(r.text)
#     if not j.get('success'):
#         raise Exception(j)
#     return j['success']['links']


def _check_url(url):
    regex = r'https://www.dropgalaxy.in/([a-zA-Z\d]{8})/file.html'
    match = re.match(regex, url)
    if match:
        return match.group(1), match.group(2)
    raise ValueError("Invalid URL: " + str(url))


def _extract(ses, url, server, id_):
    regex = (
        r'document.getElementById\(\'dlbutton\'\).href = "/d/'
        r'([a-zA-Z\d]{8})/" \+ \((\d*) % (\d*) \+ (\d*) % '
        r'(\d*)\) \+ "/(.*)";'
    )
    for _ in range(3):
        res = ses.get(url)
        if res.status_code != 500:
            break
        time.sleep(1)
    res.raise_for_status()
    meta = re.search(regex, res.text)
    if not meta:
        raise Exception('Failed to get file URL. Down?')
    num_1 = int(meta.group(2))
    num_2 = int(meta.group(3))
    num_3 = int(meta.group(4))
    num_4 = int(meta.group(5))
    enc_fname = meta.group(6)
    final_num = num_1 % num_2 + num_3 % num_4
    file_url = "https://www.dropgalaxy.in/{}/{}/{}".format(server,
                                                                id_,
                                                                final_num,
                                                                enc_fname)
    fname = unquote(enc_fname)
    return file_url, fname


# def _get_file(ref, url):
#     s.headers.update({
#         'Range': "bytes=0-",
#         'Referer': ref
#     })
#     r = s.get(url, stream=True)
#     del s.headers['Range']
#     del s.headers['Referer']
#     r.raise_for_status()
#     length = int(r.headers['Content-Length'])
#     return r, length


@pool.run_in_thread
def _generate_dropglink(url):
    ses = requests.Session()
    ses.headers.update({
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
                      "/75.0.3770.100 Safari/537.36"
    })
    server, id_ = _check_url(url)
    return _extract(ses, url, server, id_)
