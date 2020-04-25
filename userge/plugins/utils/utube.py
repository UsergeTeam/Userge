# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import asyncio
from os import path
from time import time
from math import floor

import youtube_dl as ytdl

from userge import userge, Message
from userge.utils import time_formatter, humanbytes


def yt_getInfo(link):
    try:
        x = ytdl.YoutubeDL({'no-playlist': True}).extract_info(link, download=False)
        thumb = x.get('thumbnail', '')
        formats = x.get('formats', [x])
        out = "No formats found :("
        if formats:
            out = "--U-ID   |   Reso.  |   Extension--\n"
        for i in formats:
            out += f"`{i.get('format_id','')} | {i.get('format_note', None)} | {i.get('ext', None)}`\n"
    except ytdl.utils.YoutubeDLError as e:
        return e
    else:
        return {'thumb': thumb, 'table': out, 'uploader': x.get('uploader_id', None), 'title': x.get('title', None)}


def supported(url):
    ies = ytdl.extractor.gen_extractors()
    for ie in ies:
        if ie.suitable(url) and ie.IE_NAME != 'generic':
            # Site has dedicated extractor
            return True
    return False


def tubeDl(url: list, prog, uid=None):
    _opts = {'outtmpl': path.join('downloads', '%(title)s-%(format)s.%(ext)s')}
    _quality = {'format': 'best' if not uid else str(uid)}
    _opts.update(_quality)
    try:
        x = ytdl.YoutubeDL(_opts)
        x.add_progress_hook(prog)
        dloader = x.download(url)
    except ytdl.utils.YoutubeDLError as e:
        return e
    else:
        return dloader


@userge.on_cmd("ytinfo", about={'header': "Get info from ytdl",
                                'description': 'Get information of the link without downloading',
                                'examples': '`.ytinfo link`',
                                'others': 'To get info about direct links, use `.head link`'})
async def ytinfo(message: Message):
    await message.edit("Hold on \u23f3 ..")
    _exracted = yt_getInfo(message.input_or_reply_str)
    if isinstance(_exracted, ytdl.utils.YoutubeDLError):
        await message.err(str(_exracted))
        return
    out = """
**Title** >> 
__{title}__
    
**Uploader** >>
__{uploader}__
    
{table}
    """.format_map(_exracted)
    if _exracted['thumb']:
        await message.reply_photo(_exracted['thumb'], caption=out)
        await message.delete()
    else:
        await message.edit(out)


@userge.on_cmd("ytdl", about={'header': "Download from youtube",
                              'options': {'-a': 'select the audio u-id',
                                          '-v': 'select the video u-id'},
                              'examples': ['.ytdl `link`',
                                           '`.ytdl -a12 -v120 link`']}, del_pre=True)
async def ytDown(message: Message):
    await message.edit("Hold on \u23f3 ..")
    desiredFormat = None
    startTime = time()
    if bool(message.flags):
        desiredFormat1 = str(message.flags.get('a', ''))
        desiredFormat2 = str(message.flags.get('v', ''))
        if len(message.flags) == 2:
            # 1st format must contain the video
            desiredFormat = '+'.join([desiredFormat2, desiredFormat1])
        elif len(message.flags) == 1:
            desiredFormat = desiredFormat2 or desiredFormat1

    def __progress(data: dict):
        if ((time() - startTime) % 4) > 3.9:
            if data['status'] == "downloading":
                eta = data['eta']
                speed = data['speed']
                if not (eta and speed):
                    return
                out = "**Speed** >> {}/s\n**ETA** >> {}\n".format(humanbytes(speed), time_formatter(eta))
                out += f'**File Name** >> __{data["filename"]}__\n\n'
                current = data['downloaded_bytes']
                total = data["total_bytes"]
                if current and total:
                    percentage = int(current) * 100 / int(total)
                    out += f"Progress >> {int(percentage)}%\n"
                    out += "[{}{}]".format(''.join(["█" for _ in range(floor(percentage / 5))]),
                                           ''.join(["░" for _ in range(20 - floor(percentage / 5))]))
                if message.text != out:
                    asyncio.get_event_loop().run_until_complete(message.edit(out))

    retcode = tubeDl([message.filtered_input_str], __progress, desiredFormat)
    await message.edit(str(retcode) if not retcode == 0 else f"Downloaded in {round(time() - startTime)} seconds")
