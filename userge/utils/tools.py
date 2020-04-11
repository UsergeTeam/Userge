# Copyright (C) 2020 by UsergeTeam@Telegram, < https://t.me/theUserge >.
#
# This file is part of < https://github.com/uaudith/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import asyncio
import shlex
from os.path import isfile, relpath
from glob import glob
from .logger import logging

LOG = logging.getLogger(__name__)


def humanbytes(size: int) -> str:
    if not size:
        return ""
    power = 1024
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return "{:.2f} {}B".format(size, Dic_powerN[n])


def time_formatter(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "")

    return tmp[:-2]


async def runcmd(cmd: str):
    args = shlex.split(cmd)

    process = await asyncio.create_subprocess_exec(*args,
                                                   stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await process.communicate()

    return (stdout.decode().strip(),
            stderr.decode().strip(),
            process.returncode,
            process.pid)


async def take_screen_shot(video_file: str, duration: int):
    LOG.info(f'[[[Extracting a frame from {video_file} ||| Video duration => {duration}]]]')

    ttl = duration // 2
    thumb_image_path = f"{video_file}.jpg"
    command = f"ffmpeg -ss {ttl} -i '{video_file}' -vframes 1 '{thumb_image_path}'"

    _, err, _, _ = await runcmd(command)

    if err:
        LOG.error(err)

    return thumb_image_path if thumb_image_path else None


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def get_import_path(root: str, path: str):
    seperator = '\\' if '\\' in root else '/'

    if isfile(path):
        return '.'.join(relpath(path, root).split(seperator))[:-3]

    else:
        all_paths = glob(root + path.rstrip(seperator) + f"{seperator}*.py", recursive=True)

        return sorted(
            [
                '.'.join(relpath(f, root).split(seperator))[:-3] for f in all_paths
                if not f.endswith("__init__.py")
            ]
        )
