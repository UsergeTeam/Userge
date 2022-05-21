""" upload , rename and convert telegram files """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
from pathlib import Path

from userge import userge, config, Message
from userge.utils import is_url
from userge.utils.exceptions import ProcessCanceled
from . import upload_path, upload
from ..download import tg_download, url_download

LOGGER = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd("rename", about={
    'header': "Rename telegram files",
    'flags': {
        '-d': "upload as document",
        '-wt': "without thumb"},
    'usage': "{tr}rename [flags] [new_name_with_extension] : reply to telegram media",
    'examples': "{tr}rename -d test.mp4"}, del_pre=True, check_downpath=True)
async def rename_(message: Message):
    """ rename telegram files """
    if not message.filtered_input_str:
        await message.err("new name not found!")
        return
    await message.edit("`Trying to Rename ...`")
    if message.reply_to_message and message.reply_to_message.media:
        await _handle_message(message)
    else:
        await message.err("reply to media to rename it")


@userge.on_cmd("convert", about={
    'header': "Convert telegram files",
    'usage': "reply {tr}convert to any media"}, del_pre=True, check_downpath=True)
async def convert_(message: Message):
    """ convert telegram files """
    await message.edit("`Trying to Convert ...`")
    if message.reply_to_message and message.reply_to_message.media:
        message.text = '' if message.reply_to_message.document else ". -d"
        await _handle_message(message)
    else:
        await message.err("reply to media to convert it")


@userge.on_cmd("upload", about={
    'header': "Upload files to telegram",
    'flags': {
        '-d': "upload as document",
        '-wt': "without thumb",
        '-r': "remove file after upload",
        '-df': "don't forward to log channel"},
    'usage': "{tr}upload [flags] [file or folder path | link]",
    'examples': [
        "{tr}upload -d https://speed.hetzner.de/100MB.bin | test.bin",
        "{tr}upload downloads/test.mp4"]}, del_pre=True, check_downpath=True)
async def upload_to_tg(message: Message):
    """ upload to telegram """
    path_ = message.filtered_input_str
    if not path_:
        await message.err("Input not foud!")
        return
    is_path_url = is_url(path_)
    del_path = False
    if is_path_url:
        del_path = True
        try:
            path_, _ = await url_download(message, path_)
        except ProcessCanceled:
            await message.canceled()
            return
        except Exception as e_e:  # pylint: disable=broad-except
            await message.err(str(e_e))
            return
    if "|" in path_:
        path_, file_name = path_.split("|")
        path_ = path_.strip()
        if os.path.isfile(path_):
            new_path = os.path.join(config.Dynamic.DOWN_PATH, file_name.strip())
            os.rename(path_, new_path)
            path_ = new_path
    try:
        string = Path(path_)
    except IndexError:
        await message.err("wrong syntax")
    else:
        await message.delete()
        with message.cancel_callback():
            await upload_path(message, string, del_path)


async def _handle_message(message: Message) -> None:
    try:
        dl_loc, _ = await tg_download(message, message.reply_to_message)
    except ProcessCanceled:
        await message.canceled()
    except Exception as e_e:  # pylint: disable=broad-except
        await message.err(str(e_e))
    else:
        await message.delete()
        with message.cancel_callback():
            await upload(message, Path(dl_loc), True)
