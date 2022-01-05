""" Download Youtube Video / Audio in a User friendly interface """
# --------------------------- #
#   Modded ytdl by code-rgb   #
# --------------------------- #
# Well just modifying his codes to make it compatible with lazyleech
# Src: https://github.com/code-rgb/USERGE-X
# Sadly he archived his repo but well this code is fabulous or atleast the way this works is

import glob
import os
from uuid import uuid4
from collections import defaultdict
from pathlib import Path
from re import compile as comp_regex
from time import time
import asyncio
from typing import Any, Callable
from concurrent.futures import ThreadPoolExecutor, Future
from functools import wraps, partial
from motor.frameworks.asyncio import _EXECUTOR
from .aiohttp_helper import AioHttp as get_response
import ujson
import youtube_dl
from html_telegraph_poster import TelegraphPoster
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaPhoto,
    InputMediaVideo,
)
from userge import userge, Message
from ..help import check_owner
from wget import download
from youtube_dl.utils import DownloadError, ExtractorError, GeoRestrictedError
from youtubesearchpython import VideosSearch

BASE_YT_URL = "https://www.youtube.com/watch?v="
YOUTUBE_REGEX = comp_regex(
    r"(?:youtube\.com|youtu\.be)/(?:[\w-]+\?v=|embed/|v/|shorts/)?([\w-]{11})"
)
PATH = "./ytdl/ytsearch.json"
DOWN_PATH = "./ytdl"


class YT_Search_X:
    def __init__(self):
        if not os.path.exists(PATH):
            with open(PATH, "w") as f_x:
                ujson.dump({}, f_x)
        with open(PATH) as yt_db:
            self.db = ujson.load(yt_db)

    def store_(self, rnd_id: str, results: dict):
        self.db[rnd_id] = results
        self.save()

    def save(self):
        with open(PATH, "w") as outfile:
            ujson.dump(self.db, outfile, indent=4)


__all__ = ['submit_thread', 'run_in_thread']

def submit_thread(func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Future:
    """ submit thread to thread pool """
    return _EXECUTOR.submit(func, *args, **kwargs)

def run_in_thread(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """ run in a thread """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_EXECUTOR, partial(func, *args, **kwargs))
    return wrapper

ytsearch_data = YT_Search_X()


async def get_ytthumb(videoid: str):
    thumb_quality = [
        "maxresdefault.jpg",  # Best quality
        "hqdefault.jpg",
        "sddefault.jpg",
        "mqdefault.jpg",
        "default.jpg",  # Worst quality
    ]
    thumb_link = "https://i.imgur.com/4LwPLai.png"
    for qualiy in thumb_quality:
        link = f"https://i.ytimg.com/vi/{videoid}/{qualiy}"
        if await get_response.status(link) == 200:
            thumb_link = link
            break
    return thumb_link

user_search = defaultdict(list)

@userge.on_cmd("iytdl", about={
    'header': "Advanced YTDL",
    'usage': "{tr}iytdl youtube link or query",
    'examples': "{tr}iytdl fire on fire sam smith"})
async def iytdl_inline(client: Client, message: Message):
    reply = message.reply_to_message
    input_url = None
    k = message.text.split(None, 1)
    if len(k)==2:
        input_url = k[1]
    elif reply:
        if reply.text:
            input_url = reply.text
        elif reply.caption:
            input_url = reply.caption
    if not input_url:
        x = await message.reply_text("Input or reply to a valid youtube URL")
        await asyncio.sleep(5)
        await x.delete()
        return
    x = await message.reply_text(f"🔎 Searching Youtube for: <code>'{input_url}'</code>")
    input_url = input_url.strip()
    link = get_yt_video_id(input_url)
    if link is None:
        search_ = VideosSearch(input_url, limit=15)
        resp = (search_.result()).get("result")
        if len(resp) == 0:
            await x.edit_text(f'No Results found for "{input_url}"')
            await asyncio.sleep(5)
            await x.delete()
            return
        outdata = await result_formatter(resp)
        key_ = rand_key()
        ytsearch_data.store_(key_, outdata)
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"1 / {len(outdata)}",
                        callback_data=f"ytdl_next_{key_}_1",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📜  List all",
                        callback_data=f"ytdl_listall_{key_}_1",
                    ),
                    InlineKeyboardButton(
                        text="⬇️  Download",
                        callback_data=f'ytdl_download_{outdata[1]["video_id"]}_0',
                    ),
                ],
            ]
        )
        caption = outdata[1]["message"]
        photo = outdata[1]["thumb"]
    else:
        caption, buttons = await download_button(link, body=True)
        photo = await get_ytthumb(link)
    msg = await client.send_photo(
        message.chat.id,
        photo=photo,
        caption=caption,
        reply_markup=buttons,
    )
    await x.delete()
    user_search[message.from_user.id].append([msg.chat.id, msg.message_id])


@userge.on_callback_query(
    filters.regex(pattern=r"^ytdl_download_(.*)_([\d]+|mkv|mp4|mp3)(?:_(a|v))?")
)
@check_owner
async def ytdl_download_callback(client: Client, c_q: CallbackQuery):
    yt_code = c_q.matches[0].group(1)
    choice_id = c_q.matches[0].group(2)
    downtype = c_q.matches[0].group(3)
    if str(choice_id).isdigit():
        choice_id = int(choice_id)
        if choice_id == 0:
            await c_q.answer("🔄  Processing...", show_alert=False)
            await c_q.edit_message_reply_markup(
                reply_markup=(await download_button(yt_code))
            )
            return
    startTime = time()
    choice_str, disp_str = get_choice_by_id(choice_id, downtype)
    media_type = "Video" if downtype == "v" else "Audio"
    callback_continue = f"Downloading {media_type} Please Wait..."
    callback_continue += f"\n\nFormat Code : {disp_str}"
    await c_q.answer(callback_continue, show_alert=True)
    yt_url = BASE_YT_URL + yt_code
    await c_q.edit_message_text(
        text=(
            f"**⬇️ Downloading {media_type} ...**"
            f"\n\n🔗  <b><a href='{yt_url}'>Link</a></b>\n🆔  <b>Format Code</b> : {disp_str}"
        ),
    )
    if downtype == "v":
        k = await _tubeDl(url=yt_url, starttime=startTime, uid=choice_str)
    else:
        k = await _mp3Dl(url=yt_url, starttime=startTime, uid=choice_str)
    if type(k)==list:
        await c_q.answer(k[1], show_alert=True)
        return
    _fpath = ""
    thumb_pic = None
    for _path in glob.glob(os.path.join(DOWN_PATH, str(startTime), "*")):
        if _path.lower().endswith((".jpg", ".png", ".webp")):
            thumb_pic = _path
        else:
            _fpath = _path
    if not thumb_pic and downtype == "v":
        thumb_pic = str(
            await run_in_thread(download)(await get_ytthumb(yt_code))
        )
    if downtype == "v":
        await c_q.edit_message_media(
            media=(
                InputMediaVideo(
                    media=str(Path(_fpath)),
                    caption=f"📹  <b><a href = '{yt_url}'>{Path(_fpath).name}</a></b>",
                    thumb=thumb_pic
                )
            ),
        )
    else:  # Audio
        await c_q.edit_message_media(
            media=(
                InputMediaAudio(
                    media=str(Path(_fpath)),
                    caption=f"🎵  <b><a href = '{yt_url}'>{Path(_fpath).name}</a></b>",
                    thumb=thumb_pic
                )
            ),
        )


@userge.on_callback_query(
    filters.regex(pattern=r"^ytdl_(listall|back|next|detail)_([a-z0-9]+)_(.*)")
)
@check_owner
async def ytdl_callback(_, c_q: CallbackQuery):
    choosen_btn = c_q.matches[0].group(1)
    data_key = c_q.matches[0].group(2)
    page = c_q.matches[0].group(3)
    if os.path.exists(PATH):
        with open(PATH) as f:
            view_data = ujson.load(f)
        search_data = view_data.get(data_key)
        total = len(search_data)
    else:
        return await c_q.answer(
            "Search data doesn't exists anymore, please perform search again ...",
            show_alert=True,
        )
    if choosen_btn == "back":
        index = int(page) - 1
        del_back = index == 1
        await c_q.answer()
        back_vid = search_data.get(str(index))
        await c_q.edit_message_media(
            media=(
                InputMediaPhoto(
                    media=back_vid.get("thumb"),
                    caption=back_vid.get("message"),
                )
            ),
            reply_markup=yt_search_btns(
                del_back=del_back,
                data_key=data_key,
                page=index,
                vid=back_vid.get("video_id"),
                total=total,
            ),
        )
    elif choosen_btn == "next":
        index = int(page) + 1
        if index > total:
            return await c_q.answer("That's All Folks !", show_alert=True)
        await c_q.answer()
        front_vid = search_data.get(str(index))
        await c_q.edit_message_media(
            media=(
                InputMediaPhoto(
                    media=front_vid.get("thumb"),
                    caption=front_vid.get("message"),
                )
            ),
            reply_markup=yt_search_btns(
                data_key=data_key,
                page=index,
                vid=front_vid.get("video_id"),
                total=total,
            ),
        )
    elif choosen_btn == "listall":
        await c_q.answer("View Changed to:  📜  List", show_alert=False)
        list_res = ""
        for vid_s in search_data:
            list_res += search_data.get(vid_s).get("list_view")
        telegraph = post_to_telegraph(
            a_title=f"Showing {total} youtube video results for the given query ...",
            content=list_res,
        )
        await c_q.edit_message_media(
            media=(
                InputMediaPhoto(
                    media=search_data.get("1").get("thumb"),
                )
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "↗️  Click To Open",
                            url=telegraph,
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "📰  Detailed View",
                            callback_data=f"ytdl_detail_{data_key}_{page}",
                        )
                    ],
                ]
            ),
        )
    else:  # Detailed
        index = 1
        await c_q.answer("View Changed to:  📰  Detailed", show_alert=False)
        first = search_data.get(str(index))
        await c_q.edit_message_media(
            media=(
                InputMediaPhoto(
                    media=first.get("thumb"),
                    caption=first.get("message"),
                )
            ),
            reply_markup=yt_search_btns(
                del_back=True,
                data_key=data_key,
                page=index,
                vid=first.get("video_id"),
                total=total,
            ),
        )


@run_in_thread
def _tubeDl(url: str, starttime, uid: str):
    ydl_opts = {
        "addmetadata": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "outtmpl": os.path.join(
            DOWN_PATH, str(starttime), "%(title)s-%(format)s.%(ext)s"
        ),
        "format": uid,
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "postprocessors": [
            {"key": "FFmpegMetadata"}
            # ERROR R15: Memory quota vastly exceeded
            # {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
        ],
        "quiet": True,
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            x = ydl.download([url])
    except DownloadError as e:
        return [e]
    except GeoRestrictedError:
        return ["ERROR: The uploader has not made this video available in your country"]
    else:
        return x


@run_in_thread
def _mp3Dl(url: str, starttime, uid: str):
    _opts = {
        "outtmpl": os.path.join(DOWN_PATH, str(starttime), "%(title)s.%(ext)s"),
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "format": "bestaudio/best",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": uid,
            },
            {"key": "EmbedThumbnail"},  # ERROR: Conversion failed!
            {"key": "FFmpegMetadata"},
        ],
        "quiet": True,
    }
    try:
        with youtube_dl.YoutubeDL(_opts) as ytdl:
            dloader = ytdl.download([url])
    except Exception as y_e:
        return [y_e]
    else:
        return dloader


def get_yt_video_id(url: str):
    # https://regex101.com/r/c06cbV/1
    match = YOUTUBE_REGEX.search(url)
    if match:
        return match.group(1)


# Based on https://gist.github.com/AgentOak/34d47c65b1d28829bb17c24c04a0096f
def get_choice_by_id(choice_id, media_type: str):
    if choice_id == "mkv":
        # default format selection
        choice_str = "bestvideo+bestaudio/best"
        disp_str = "best(video+audio)"
    elif choice_id == "mp4":
        # Download best Webm / Mp4 format available or any other best if no mp4
        # available
        choice_str = "bestvideo[ext=webm]+251/bestvideo[ext=mp4]+(258/256/140/bestaudio[ext=m4a])/bestvideo[ext=webm]+(250/249)/best"
        disp_str = "best(video+audio)[webm/mp4]"
    elif choice_id == "mp3":
        choice_str = "320"
        disp_str = "320 Kbps"
    else:
        disp_str = str(choice_id)
        if media_type == "v":
            # mp4 video quality + best compatible audio
            choice_str = disp_str + "+(258/256/140/bestaudio[ext=m4a])/best"
        else:  # Audio
            choice_str = disp_str
    return choice_str, disp_str


async def result_formatter(results: list):
    output = {}
    for index, r in enumerate(results, start=1):
        upld = r.get("channel")
        title = f'<a href={r.get("link")}><b>{r.get("title")}</b></a>\n'
        out = title
        if r.get("descriptionSnippet"):
            out += "<code>{}</code>\n\n".format(
                "".join(x.get("text") for x in r.get("descriptionSnippet"))
            )
        out += f'<b>❯  Duration:</b> {r.get("accessibility").get("duration")}\n'
        views = f'<b>❯  Views:</b> {r.get("viewCount").get("short")}\n'
        out += views
        out += f'<b>❯  Upload date:</b> {r.get("publishedTime")}\n'
        if upld:
            out += "<b>❯  Uploader:</b> "
            out += f'<a href={upld.get("link")}>{upld.get("name")}</a>'
        v_deo_id = r.get("id")
        thumb = f"https://i.ytimg.com/vi/{v_deo_id}/maxresdefault.jpg"
        output[index] = dict(
            message=out,
            thumb=thumb,
            video_id=v_deo_id,
            list_view=f'<img src={thumb}><b><a href={r.get("link")}>{index}. {r.get("accessibility").get("title")}</a></b><br>',
        )

    return output


def yt_search_btns(
    data_key: str, page: int, vid: str, total: int, del_back: bool = False
):
    buttons = [
        [
            InlineKeyboardButton(
                text="⬅️  Back",
                callback_data=f"ytdl_back_{data_key}_{page}",
            ),
            InlineKeyboardButton(
                text=f"{page} / {total}",
                callback_data=f"ytdl_next_{data_key}_{page}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📜  List all",
                callback_data=f"ytdl_listall_{data_key}_{page}",
            ),
            InlineKeyboardButton(
                text="⬇️  Download",
                callback_data=f"ytdl_download_{vid}_0",
            ),
        ],
    ]
    if del_back:
        buttons[0].pop(0)
    return InlineKeyboardMarkup(buttons)


@run_in_thread
def download_button(vid: str, body: bool = False):
    try:
        vid_data = youtube_dl.YoutubeDL({"no-playlist": True}).extract_info(
            BASE_YT_URL + vid, download=False
        )
    except ExtractorError:
        vid_data = {"formats": []}
    buttons = [
        [
            InlineKeyboardButton(
                "⭐️ BEST - 📹 MKV", callback_data=f"ytdl_download_{vid}_mkv_v"
            ),
            InlineKeyboardButton(
                "⭐️ BEST - 📹 WebM/MP4",
                callback_data=f"ytdl_download_{vid}_mp4_v",
            ),
        ]
    ]
    # ------------------------------------------------ #
    qual_dict = defaultdict(lambda: defaultdict(int))
    qual_list = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p"]
    audio_dict = {}
    # ------------------------------------------------ #
    for video in vid_data["formats"]:

        fr_note = video.get("format_note")
        fr_id = int(video.get("format_id"))
        fr_size = video.get("filesize")
        if video.get("ext") == "mp4":
            for frmt_ in qual_list:
                if fr_note in (frmt_, frmt_ + "60"):
                    qual_dict[frmt_][fr_id] = fr_size
        if video.get("acodec") != "none":
            bitrrate = int(video.get("abr", 0))
            if bitrrate != 0:
                audio_dict[
                    bitrrate
                ] = f"🎵 {bitrrate}Kbps ({humanbytes(fr_size) or 'N/A'})"

    video_btns = []
    for frmt in qual_list:
        frmt_dict = qual_dict[frmt]
        if len(frmt_dict) != 0:
            frmt_id = sorted(list(frmt_dict))[-1]
            frmt_size = humanbytes(frmt_dict.get(frmt_id)) or "N/A"
            video_btns.append(
                InlineKeyboardButton(
                    f"📹 {frmt} ({frmt_size})",
                    callback_data=f"ytdl_download_{vid}_{frmt_id}_v",
                )
            )
    buttons += sublists(video_btns, width=2)
    buttons += [
        [
            InlineKeyboardButton(
                "⭐️ BEST - 🎵 320Kbps - MP3", callback_data=f"ytdl_download_{vid}_mp3_a"
            )
        ]
    ]
    buttons += sublists(
        [
            InlineKeyboardButton(
                audio_dict.get(key_), callback_data=f"ytdl_download_{vid}_{key_}_a"
            )
            for key_ in sorted(audio_dict.keys())
        ],
        width=2,
    )
    if body:
        vid_body = f"<b><a href='{vid_data.get('webpage_url')}'>{vid_data.get('title')}</a></b>"
        return vid_body, InlineKeyboardMarkup(buttons)
    return InlineKeyboardMarkup(buttons)


def rand_key():
    return str(uuid4())[:8]


def post_to_telegraph(a_title: str, content: str) -> str:
    """ Create a Telegram Post using HTML Content """
    post_client = TelegraphPoster(use_api=True)
    auth_name = "LazyLeech"
    post_client.create_api_token(auth_name)
    post_page = post_client.post(
        title=a_title,
        author=auth_name,
        author_url="https://t.me/lostb053",
        text=content,
    )
    return post_page["url"]


def humanbytes(size: float) -> str:
    """ humanize size """
    if not size:
        return ""
    power = 1024
    t_n = 0
    power_dict = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        t_n += 1
    return "{:.2f} {}B".format(size, power_dict[t_n])


def sublists(input_list: list, width: int = 3):
    return [input_list[x : x + width] for x in range(0, len(input_list), width)]