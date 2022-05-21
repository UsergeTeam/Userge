""" spotdl downloader """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

from pathlib import Path
from typing import Union

from spotdl.download.downloader import DownloadManager
from spotdl.search import spotifyClient
from spotdl.search.songObj import SongObj

from userge import userge, Message, pool
from ..upload import audio_upload


def init_client() -> None:
    try:
        spotifyClient.initialize(
            clientId='4fe3fecfe5334023a1472516cc99d805',
            clientSecret='0f02b7c483c04257984695007a4a8d5c'
        )
    except Exception:
        pass


async def download_track(url: Union[str, SongObj]) -> Path:
    init_client()
    song = url
    if not isinstance(url, SongObj):
        song = await pool.run_in_thread(SongObj.from_url)(song)
    return await DownloadManager().download_song(song)


@userge.on_cmd("stdl", about={
    'header': "Spotify Track Downloader",
    'description': "Download Songs via Spotify Links",
    'usage': "{tr}stdl [Spotify Link]",
    'examples': "{tr}stdl https://open.spotify.com/track/0Cy7wt6IlRfBPHXXjmZbcP"})
async def spotify_dl(message: Message) -> None:
    link = message.input_str
    await message.edit(f"`Downloading: {link} ...`")
    try:
        track = await download_track(link)
    except Exception as e:
        return await message.err(str(e))
    await audio_upload(message, track, True)
