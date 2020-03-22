import asyncio
import os
import shlex

from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

from .logger import logging

LOG = logging.getLogger(__name__)


async def runcmd(cmd):
    args = shlex.split(cmd)

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    return stdout.decode().strip(), stderr.decode().strip(), process.returncode


async def take_screen_shot(video_file, duration):
    LOG.info(f'[[[Extracting a frame from {video_file} ||| Video duration => {duration}]]]')
    ttl = duration // 2
    thumb_image_path = f"{video_file}.jpg"
    # -filter:v scale=90:-1
    command = f"ffmpeg -ss {ttl} -i '{video_file}' -vframes 1 '{thumb_image_path}'"
    _, err, rcode = await runcmd(command)
    if err:
        LOG.error(err)

    return thumb_image_path if thumb_image_path else None


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'
