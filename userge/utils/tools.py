# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import importlib
import re
import shlex
from os.path import basename, join, exists
from typing import Tuple, List, Optional, Iterator, Union

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import userge

_LOG = userge.logging.getLogger(__name__)

_BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)]\[buttonurl:/{0,2}(.+?)(:same)?])")
_PTN_SPLIT = re.compile(r'(\.\d+|\.|\d+)')
_PTN_URL = re.compile(r"(?:https?|ftp)://[^|\s]+\.[^|\s]+")


def is_url(url: str) -> bool:
    return bool(_PTN_URL.match(url))


def sort_file_name_key(file_name: str) -> tuple:
    """ sort key for file names """
    if not isinstance(file_name, str):
        file_name = str(file_name)
    return tuple(_sort_algo(_PTN_SPLIT.split(file_name.lower())))


# this algo doesn't support signed values
def _sort_algo(data: List[str]) -> Iterator[Union[str, float]]:
    """ sort algo for file names """
    p1 = 0.0
    for p2 in data:
        # skipping null values
        if not p2:
            continue

        # first letter of the part
        c = p2[0]

        # checking c is a digit or not
        # if yes, p2 should not contain any non digits
        if c.isdigit():
            # p2 should be [0-9]+
            # so c should be 0-9
            if c == '0':
                # add padding
                # this fixes `a1` and `a01` messing
                if isinstance(p1, str):
                    yield 0.0
                yield c

            # converting to float
            p2 = float(p2)

            # add padding
            if isinstance(p1, float):
                yield ''

        # checking p2 is `.[0-9]+` or not
        elif c == '.' and len(p2) > 1 and p2[1].isdigit():
            # p2 should be `.[0-9]+`
            # so converting to float
            p2 = float(p2)

            # add padding
            if isinstance(p1, str):
                yield 0.0
            yield c

        # add padding if previous and current both are strings
        if isinstance(p1, str) and isinstance(p2, str):
            yield 0.0

        yield p2
        # saving current value for later use
        p1 = p2


def get_file_id_of_media(message: 'userge.Message') -> Optional[str]:
    """ get file_id """
    file_ = message.audio or message.animation or message.photo \
        or message.sticker or message.voice or message.video_note \
        or message.video or message.document
    if file_:
        return file_.file_id
    return None


def humanbytes(size: float) -> str:
    """ humanize size """
    if not size:
        return "0 B"
    power = 1024
    t_n = 0
    power_dict = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        t_n += 1
    return "{:.2f} {}B".format(size, power_dict[t_n])


def time_formatter(seconds: float) -> str:
    """ humanize time """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "")
    return tmp[:-2]


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """ run command in terminal """
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(*args,
                                                   stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    return (stdout.decode('utf-8', 'replace').strip(),
            stderr.decode('utf-8', 'replace').strip(),
            process.returncode,
            process.pid)


async def take_screen_shot(video_file: str, duration: int, path: str = '') -> Optional[str]:
    """ take a screenshot """
    _LOG.info('Extracting a frame from %s ||| Video duration => %s', video_file, duration)

    ttl = duration // 2
    thumb_image_path = path or join(userge.config.Dynamic.DOWN_PATH, f"{basename(video_file)}.jpg")
    command = f'''ffmpeg -ss {ttl} -i "{video_file}" -vframes 1 "{thumb_image_path}"'''

    err = (await runcmd(command))[1]
    if err:
        _LOG.error(err)

    return thumb_image_path if exists(thumb_image_path) else None


def parse_buttons(markdown_note: str) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
    """ markdown_note to string and buttons """
    prev = 0
    note_data = ""
    buttons: List[Tuple[str, str, bool]] = []
    for match in _BTN_URL_REGEX.finditer(markdown_note):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and markdown_note[to_check] == "\\":
            n_escapes += 1
            to_check -= 1
        if n_escapes % 2 == 0:
            buttons.append((match.group(2), match.group(3), bool(match.group(4))))
            note_data += markdown_note[prev:match.start(1)]
            prev = match.end(1)
        else:
            note_data += markdown_note[prev:to_check]
            prev = match.start(1) - 1
    note_data += markdown_note[prev:]
    keyb: List[List[InlineKeyboardButton]] = []
    for btn in buttons:
        if btn[2] and keyb:
            keyb[-1].append(InlineKeyboardButton(btn[0], url=btn[1]))
        else:
            keyb.append([InlineKeyboardButton(btn[0], url=btn[1])])
    return note_data.strip(), InlineKeyboardMarkup(keyb) if keyb else None


def is_command(cmd: str) -> bool:
    commands = userge.userge.manager.loaded_commands
    key = userge.config.CMD_TRIGGER + cmd
    _key = userge.config.SUDO_TRIGGER + cmd

    is_cmd = False
    if cmd in commands:
        is_cmd = True
    elif key in commands:
        is_cmd = True
    elif _key in commands:
        is_cmd = True
    return is_cmd


def extract_entities(message: Message, typeofentity: List[str]) -> List[str]:
    """ gets a message and returns a list of entity_type in the message
    """
    tero = []
    entities = message.entities or message.caption_entities or []
    text = message.text or message.caption or ""
    for entity in entities:
        url = None
        cet = entity.type
        if entity.type in [
            "url",
            "mention",
            "hashtag",
            "cashtag",
            "bot_command",
            "url",
            "email",
            "phone_number",
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "spoiler",
            "code",
            "pre",
        ]:
            offset = entity.offset
            length = entity.length
            url = text[offset:offset + length]

        elif entity.type == "text_link":
            url = entity.url

        elif entity.type == "text_mention":
            url = entity.user

        if url and cet in typeofentity:
            tero.append(url)
    return tero


def get_custom_import_re(req_module):
    """ import custom modules dynamically """
    try:
        return importlib.import_module(req_module)
    except ModuleNotFoundError:
        _LOG.warning(f"please fix your requirements.txt file [{req_module}]")
        raise
