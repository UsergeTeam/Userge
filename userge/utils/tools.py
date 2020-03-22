import asyncio
import os
import shlex

from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

from .logger import logging

LOG = logging.getLogger(__name__)


async def humanbytes(size):
    if not size:
        return ""

    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}

    while size > power:
        size /= power
        n += 1

    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


async def time_formatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")

    return tmp[:-2]


async def runcmd(cmd):
    args = shlex.split(cmd)

    process = await asyncio.create_subprocess_exec(*args,
                                                   stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await process.communicate()

    return (stdout.decode().strip(),
            stderr.decode().strip(),
            process.returncode,
            process.pid)


async def take_screen_shot(video_file, duration):
    LOG.info(f'[[[Extracting a frame from {video_file} ||| Video duration => {duration}]]]')
    ttl = duration // 2
    thumb_image_path = f"{video_file}.jpg"
    # -filter:v scale=90:-1
    command = f"ffmpeg -ss {ttl} -i '{video_file}' -vframes 1 '{thumb_image_path}'"
    _, err, rcode, _ = await runcmd(command)
    
    if err:
        LOG.error(err)

    return thumb_image_path if thumb_image_path else None


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'
