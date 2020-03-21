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

    power = 2 ** 10
    n = 0

    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}

    while size > power:
        size /= power
        n += 1

    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


async def TimeFormatter(milliseconds: int) -> str:
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

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    return stdout.decode().strip(), stderr.decode().strip(), process.returncode


async def take_screen_shot(video_file, duration):
    if duration >= 10:
        ttl = duration // 2
        thumb_image_path = f"{video_file}.jpg"
        # -filter:v scale=90:-1
        command = f"ffmpeg -ss {ttl} -i {video_file} -vframes 1 {thumb_image_path}"

        _, err, rcode = await runcmd(command)

        if not rcode:
            LOG.error(err)

        if os.path.lexists(thumb_image_path):
            metadata = extractMetadata(createParser(thumb_image_path))
            height = 0

            if metadata.has("height"):
                height = metadata.get("height")

            Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
            img = Image.open(thumb_image_path)
            img.resize((320, height))
            img.save(thumb_image_path, "JPEG")

            LOG.info(thumb_image_path)

            return thumb_image_path
    return None


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'
