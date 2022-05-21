""" deezloader """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import re
import shutil
from pathlib import Path

import deezloader  # pylint: disable=W0406
from deezloader.exceptions import NoDataApi

from userge import userge, Message, pool
from . import ARL_TOKEN
from ..upload import doc_upload, audio_upload

Clogger = userge.getCLogger(__name__)

TEMP_PATH = 'deezdown_temp/'
REX = re.compile(r"https?:\/\/(open\.spotify|www\.deezer)\.com\/"
                 r"(track|album|playlist)\/[A-Z0-9a-z]{3,}")
ARL_HELP = """**Oops, Time to Help Yourself**
[Here Help Yourself](https://www.google.com/search?q=how+to+get+deezer+arl+token)

After getting Arl token Config `ARL_TOKEN` var in heroku"""


@userge.on_cmd("deezload", about={
    'header': "DeezLoader for Userge",
    'description': "Download Songs/Albums/Playlists via "
                   "Spotify or Deezer Links. "
                   "\n<b>NOTE:</b> Music Quality is optional",
    'flags': {'-dsong': "Download a Song by passing Artist Name and Song Name",
              '-zip': "Get a zip archive for Albums/Playlist Download"},
    'options': "Available Sound Quality: <code>FLAC | MP3_320 | MP3_256 | MP3_128</code>",
    'usage': "{tr}deezload [flag] [link | quality (default MP3_320)]",
    'examples': "{tr}deezload https://www.deezer.com/track/142750222 \n"
                "{tr}deezload https://www.deezer.com/track/3824710 FLAC \n"
                "{tr}deezload https://www.deezer.com/album/1240787 FLAC \n"
                "{tr}deezload -zip https://www.deezer.com/album/1240787 \n"
                "{tr}deezload -dsong Ed Sheeran-Shape of You"})
async def deezload(message: Message):
    cmd = str(message.text)[0]
    if not os.path.exists(TEMP_PATH):
        os.makedirs(TEMP_PATH)
    await message.edit("Checking your Token.")
    if ARL_TOKEN is None:
        await message.edit(ARL_HELP, disable_web_page_preview=True)
        return
    try:
        loader = deezloader.Login(ARL_TOKEN)
    except Exception as er:
        await message.edit(er)
        await Clogger.log(f"#ERROR\n\n{er}")
        return

    flags = list(message.flags)
    if '-zip' not in flags:
        to_zip = False
    else:
        to_zip = True
    d_quality = "MP3_320"
    if not message.filtered_input_str:
        await message.edit("Olá Peru Master🙂, Tell me how to download `Nothing`")
        return
    input_ = message.filtered_input_str
    if '-dsong' not in flags:
        try:
            input_link, quality = input_.split()
        except ValueError:
            if len(input_.split()) == 1:
                input_link = input_
                quality = d_quality
            else:
                await message.edit("Invalid Syntax Detected. 🙂")
                return
        if not REX.search(input_link):
            await message.edit("As per my Blek Mejik Regex, this link is not supported.")
            return
    else:
        try:
            artist, song, quality = input_.split('-')
        except ValueError:
            if len(input_.split("-")) == 2:
                artist, song = input_.split('-')
                quality = d_quality
            else:
                await message.edit(f"🙂K!! Check `{cmd}help deezload`")
                return
        await message.edit(f"Searching Results for {song}")
        try:
            track = await pool.run_in_thread(loader.download_name)(
                artist=artist.strip(),
                song=song.strip(),
                output=TEMP_PATH,
                quality=quality.strip(),
                recursive_quality=True,
                recursive_download=True,
                not_interface=True
            )
            await message.edit("Song found, Now Uploading 📤", del_in=5)
            await audio_upload(message, Path(track), True)
        except Exception as e_r:
            await message.edit("Song not Found 🚫")
            await Clogger.log(f"#ERROR\n\n{e_r}")
        await message.delete()
        shutil.rmtree(TEMP_PATH, ignore_errors=True)
        return

    try:
        if 'track/' in input_link:
            await proper_trackdl(input_link, quality, message, loader, TEMP_PATH)
        else:
            await batch_dl(input_link, quality, message, loader, TEMP_PATH, to_zip)
    except NoDataApi as nd:
        await message.edit("No Data is available for input link")
        await Clogger.log(f"#ERROR\n\n{nd}")
    except Exception as e_r:
        await Clogger.log(f"#ERROR\n\n{e_r}")

    await message.delete()
    shutil.rmtree(TEMP_PATH, ignore_errors=True)


async def proper_trackdl(link, qual, msg, client, dir_):
    if 'spotify' in link:
        await msg.edit("Download Started. Wait Plox.")
        track = await pool.run_in_thread(client.download_trackspo)(
            link,
            output=dir_,
            quality=qual,
            recursive_quality=True,
            recursive_download=True,
            not_interface=True
        )
        await msg.edit("Download Successful.", del_in=5)
        await audio_upload(msg, Path(track), True)
    elif 'deezer' in link:
        await msg.edit("Download Started. Wait Plox.")
        track = await pool.run_in_thread(client.download_trackdee)(
            link,
            output=dir_,
            quality=qual,
            recursive_quality=True,
            recursive_download=True,
            not_interface=True
        )
        await msg.edit("Download Successful.", del_in=5)
        await audio_upload(msg, Path(track), True)


async def batch_dl(link, qual, msg, client, dir_, allow_zip):
    if 'spotify' in link:
        if 'album/' in link:
            await msg.edit("Trying to download album 🤧")
            if allow_zip:
                _, zip_ = await pool.run_in_thread(client.download_albumspo)(
                    link,
                    output=dir_,
                    quality=qual,
                    recursive_quality=True,
                    recursive_download=True,
                    not_interface=True,
                    zips=True
                )
                await msg.edit("Sending as Zip File 🗜")
                await doc_upload(msg, Path(zip_), True)
            else:
                album_list = await pool.run_in_thread(client.download_albumspo)(
                    link,
                    output=dir_,
                    quality=qual,
                    recursive_quality=True,
                    recursive_download=True,
                    not_interface=True,
                    zips=False)
                await msg.edit("Uploading Tracks 📤", del_in=5)
                for track in album_list:
                    await audio_upload(msg, Path(track), True)
        if 'playlist/' in link:
            await msg.edit("Trying to download Playlist 🎶")
            if allow_zip:
                _, zip_ = await pool.run_in_thread(client.download_playlistspo)(
                    link,
                    output=dir_,
                    quality=qual,
                    recursive_quality=True,
                    recursive_download=True,
                    not_interface=True,
                    zips=True
                )
                await msg.edit("Sending as Zip 🗜", del_in=5)
                await doc_upload(msg, Path(zip_), True)
            else:
                album_list = await pool.run_in_thread(client.download_playlistspo)(
                    link,
                    output=dir_,
                    quality=qual,
                    recursive_quality=True,
                    recursive_download=True,
                    not_interface=True,
                    zips=False
                )
                await msg.edit("Uploading Tracks 📤", del_in=5)
                for track in album_list:
                    await audio_upload(msg, Path(track), True)

    if 'deezer' in link:
        if 'album/' in link:
            await msg.edit("Trying to download album 🤧")
            if allow_zip:
                _, zip_ = await pool.run_in_thread(client.download_albumdee)(
                    link,
                    output=dir_,
                    quality=qual,
                    recursive_quality=True,
                    recursive_download=True,
                    not_interface=True,
                    zips=True
                )
                await msg.edit("Uploading as Zip File 🗜", del_in=5)
                await doc_upload(msg, Path(zip_), True)
            else:
                album_list = await pool.run_in_thread(client.download_albumdee)(
                    link,
                    output=dir_,
                    quality=qual,
                    recursive_quality=True,
                    recursive_download=True,
                    not_interface=True,
                    zips=False
                )
                await msg.edit("Uploading Tracks 📤", del_in=5)
                for track in album_list:
                    await audio_upload(msg, Path(track), True)
        elif 'playlist/' in link:
            await msg.edit("Trying to download Playlist 🎶")
            if allow_zip:
                _, zip_ = await pool.run_in_thread(client.download_playlistdee)(
                    link,
                    output=dir_,
                    quality=qual,
                    recursive_quality=True,
                    recursive_download=True,
                    not_interface=True,
                    zips=True
                )
                await msg.edit("Sending as Zip File 🗜", del_in=5)
                await doc_upload(msg, Path(zip_), True)
            else:
                album_list = await pool.run_in_thread(client.download_playlistdee)(
                    link,
                    output=dir_,
                    quality=qual,
                    recursive_quality=True,
                    recursive_download=True,
                    not_interface=True,
                    zips=False
                )
                await msg.edit("Uploading Tracks 📤", del_in=5)
                for track in album_list:
                    await audio_upload(msg, Path(track), True)
