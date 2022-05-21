#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
#
#  Copyright (C) 2020 @UniBorg
# 0) original: https://github.com/SpEcHiDe/UniBorg/raw/master/stdplugins/google_photos.py
# വിവരണം അടിച്ചുമാറ്റിക്കൊണ്ട് പോകുന്നവർ ക്രെഡിറ്റ് വെച്ചാൽ സന്തോഷമേ ഉള്ളു..!
#
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

""" Google Photos """

import asyncio
import os
import re
from mimetypes import guess_type

import aiofiles
import aiohttp
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client

from userge import userge, Message, config
from userge.plugins.misc.download import tg_download, url_download
from userge.utils import progress
from .. import google_photos

# setup the gPhotos v1 API
OAUTH_SCOPE = [
    "https://www.googleapis.com/auth/photoslibrary",
    "https://www.googleapis.com/auth/photoslibrary.sharing"
]
# Redirect URI for installed apps, can be left as is
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
PHOTOS_BASE_URI = "https://photoslibrary.googleapis.com"

TOKEN_FILE_NAME = os.path.join(config.Dynamic.DOWN_PATH, "gPhoto_credentials_UserGe.json")

LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd("gpsetup", about={'header': "setup gphotos"})
async def setup_google_photos(message: Message):
    if (
        google_photos.G_PHOTOS_CLIENT_ID is None
        or google_photos.G_PHOTOS_CLIENT_SECRET is None
    ):
        await message.err("first fill gphoto id and secret")
        return
    creds = await check_creds(message)
    if not creds:
        await message.edit("**Check** `log channel`")
        await create_token_file()
        await message.edit("CREDS created. 😕😖😖")
    else:
        await message.edit("CREDS already created. 😕")


async def create_token_file():
    # Run through the OAuth flow and retrieve credentials
    flow = client.OAuth2WebServerFlow(
        google_photos.G_PHOTOS_CLIENT_ID,
        google_photos.G_PHOTOS_CLIENT_SECRET,
        OAUTH_SCOPE,
        redirect_uri=REDIRECT_URI
    )
    authorize_url = flow.step1_get_authorize_url()
    async with userge.conversation(config.LOG_CHANNEL_ID, timeout=150) as conv:
        await conv.send_message(
            "Go to the following link in "
            f"your browser: {authorize_url} and reply the code"
        )
        response = await conv.get_response(mark_read=True)
        code = response.text.strip()
        credentials = flow.step2_exchange(code)
        storage = file.Storage(TOKEN_FILE_NAME)
        storage.put(credentials)
        imp_gsem = await conv.send_document(document=TOKEN_FILE_NAME)
        await imp_gsem.reply_text(
            "#GPHOTOS #setup #completed\n\n"
            "please set <code>G_PHOTOS_AUTH_TOKEN_ID</code> = "
            f"<u>{imp_gsem.message_id}</u> ..!"
            "\n\n<i>This is only required, "
            "if you are running in an ephimeral file-system</i>.",
            parse_mode="html"
        )
        return storage


async def check_creds(message):
    if google_photos.G_PHOTOS_AUTH_TOKEN_ID:
        confidential_message = await message.client.get_messages(
            chat_id=config.LOG_CHANNEL_ID,
            message_ids=google_photos.G_PHOTOS_AUTH_TOKEN_ID,
            replies=0
        )
        if confidential_message and confidential_message.document:
            await confidential_message.download(file_name=TOKEN_FILE_NAME)
    if os.path.exists(TOKEN_FILE_NAME):
        pho_storage = file.Storage(TOKEN_FILE_NAME)
        creds = pho_storage.get()
        if not creds or creds.invalid:
            return None
        creds.refresh(Http())
        return creds
    return None


@userge.on_cmd("gpupload", about={
    'header': "upload files to gphoto",
    'usage': "{tr}gpupload [link | path | reply to media]",
    'examples': [
        "{tr}gpupload downloads/img.jpg",
        "{tr}gpupload https://imgur.com/download/Inyeb1S"]}, check_down_path=True)
async def upload_google_photos(message: Message):
    creds = await check_creds(message)
    if not creds:
        await message.edit_text("😏 <code>gpsetup</code> first 😡😒😒", parse_mode="html")
        return
    path_ = ""
    if message.input_str:
        if re.search(r"(?:https?|ftp)://[^|\s]+\.[^|\s]+", message.input_str):
            path_, _ = await url_download(message, message.input_str)
        elif os.path.exists(message.input_str):
            path_ = message.input_str
    elif message.reply_to_message and message.reply_to_message.media:
        path_, _ = await tg_download(message, message.reply_to_message)
    if not path_:
        await message.err("what should i upload ?")
        return
    await message.edit("`proccesing ...`")
    service = build("photoslibrary", "v1", http=creds.authorize(Http()))
    file_name, mime_type, file_size = file_ops(path_)
    await message.edit_text("file downloaded, gathering upload informations ")
    async with aiohttp.ClientSession() as session:
        headers = {
            "Content-Length": "0",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Content-Type": mime_type,
            "X-Goog-Upload-File-Name": file_name,
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Raw-Size": str(file_size),
            "Authorization": "Bearer " + creds.access_token,
        }
        # Step 1: Initiating an upload session
        step_one_response = await session.post(f"{PHOTOS_BASE_URI}/v1/uploads", headers=headers)
        if step_one_response.status != 200:
            await message.edit_text((await step_one_response.text()))
            return
        step_one_resp_headers = step_one_response.headers
        # Step 2: Saving the session URL
        real_upload_url = step_one_resp_headers.get("X-Goog-Upload-URL")
        upload_granularity = int(step_one_resp_headers.get("X-Goog-Upload-Chunk-Granularity"))
        # https://t.me/c/1279877202/74
        number_of_req_s = int(file_size / upload_granularity)
        loop = asyncio.get_event_loop()
        async with aiofiles.open(path_, mode="rb") as f_d:
            for i in range(number_of_req_s):
                current_chunk = await f_d.read(upload_granularity)
                offset = i * upload_granularity
                part_size = len(current_chunk)
                headers = {
                    "Content-Length": str(part_size),
                    "X-Goog-Upload-Command": "upload",
                    "X-Goog-Upload-Offset": str(offset),
                    "Authorization": "Bearer " + creds.access_token,
                }
                response = await session.post(real_upload_url, headers=headers, data=current_chunk)
                loop.create_task(progress(offset + part_size, file_size,
                                          message, "uploading(gphoto)🧐?"))
                # LOG.info(response.headers)
                # https://github.com/SpEcHiDe/UniBorg/commit/8267811b1248c00cd1e34041e2ae8c82b207970f
            current_chunk = await f_d.read(upload_granularity)
            # https://t.me/c/1279877202/74
            headers = {
                "Content-Length": str(len(current_chunk)),
                "X-Goog-Upload-Command": "upload, finalize",
                "X-Goog-Upload-Offset": str(number_of_req_s * upload_granularity),
                "Authorization": "Bearer " + creds.access_token,
            }
            response = await session.post(real_upload_url, headers=headers, data=current_chunk)
        final_response_text = await response.text()
    await message.edit_text("uploaded to Google Photos, getting FILE URI 🤔🤔")
    response_create_album = service.mediaItems().batchCreate(
        body={
            "newMediaItems": [{
                "description": "uploaded using @UniBorg v7",
                "simpleMediaItem": {
                    "fileName": file_name,
                    "uploadToken": final_response_text
                }
            }]
        }
    ).execute()
    try:
        photo_url = response_create_album.get(
            "newMediaItemResults")[0].get("mediaItem").get("productUrl")
        await message.edit_text(photo_url)
    except Exception as e:  # pylint: disable=broad-except
        await message.edit_text(str(e))


# Get mime type and name of given file
def file_ops(file_path):
    file_size = os.stat(file_path).st_size
    mime_type = guess_type(file_path)[0]
    mime_type = mime_type if mime_type else "text/plain"
    file_name = file_path.split("/")[-1]
    return file_name, mime_type, file_size
