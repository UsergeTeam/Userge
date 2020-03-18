import shlex
import asyncio
from .logger import logging
import os
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

logger = logging.getLogger(__name__)


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
        out, err, rcode = await runcmd(command)
        if not rcode:
            logger.error(err)
        if os.path.lexists(thumb_image_path):
            metadata = extractMetadata(createParser(thumb_image_path))
            height = 0
            if metadata.has("height"):
                height = metadata.get("height")
            Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
            img = Image.open(thumb_image_path)
            img.resize((320, height))
            img.save(thumb_image_path, "JPEG")
            logger.info(thumb_image_path)
            return thumb_image_path
    return None


