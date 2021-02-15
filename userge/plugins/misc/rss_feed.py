""" Rss Feed Plugin to get regular updates from Feed """

# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import wget
import asyncio
import feedparser
from datetime import datetime, timedelta
from dateutil import parser

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ChatWriteForbidden, ChannelPrivate, UserNotParticipant, ChatIdInvalid
)

from userge.utils.exceptions import UsergeBotNotFound
from userge import userge, Message, Config, logging, get_collection, pool

RSS_CHAT_ID = [int(x) for x in os.environ.get("RSS_CHAT_ID", str(Config.LOG_CHANNEL_ID)).split()]
_LOG = logging.getLogger(__name__)

RSS_DICT = {}
PUBLISHED_DICT = {}

RSS_COLLECTION = get_collection("RSS_COLLECTION")  # Changed Collection Name cuz of Messsssss
TASK_RUNNING = False


async def _init():
    async for i in RSS_COLLECTION.find():
        RSS_DICT[i['url']] = i['last_updated']
        PUBLISHED_DICT[i['url']] = i['published']


async def add_new_feed(url: str, l_u: datetime) -> str:
    if url in RSS_DICT:
        out_str = "`Url is matched in Existing Feed Database.`"
    else:
        parse_time = (parser.parse(l_u) + timedelta(hours=5, minutes=30)).replace(tzinfo=None)
        out_str = f"""
#ADDED_NEW_FEED_URL

\t\t**FEED URL:** `{url}`
\t\t**LAST UPDATED:** `{parse_time}`
"""
        RSS_DICT[url] = parse_time
        PUBLISHED_DICT[url] = parse_time
        if not TASK_RUNNING:
            asyncio.get_event_loop().create_task(rss_worker())
        await RSS_COLLECTION.update_one(
            {'url': url}, {"$set": {'last_updated': parse_time, 'published': parse_time}},
            upsert=True
        )
    return out_str


async def delete_feed(url: str) -> str:
    if url in RSS_DICT:
        out_str = f"""
#DELETED_FEED_URL

\t\t**FEED_URL:** `{url}`
"""
        del RSS_DICT[url]
        del PUBLISHED_DICT[url]
        await RSS_COLLECTION.delete_one({'url': url})
    else:
        out_str = "`This Url is not in my database.`"
    return out_str


async def send_new_post(entries):
    title = entries.get('title')
    link = entries.get('link')
    time = entries.get('published')
    thumb = None
    author = None
    author_link = None

    thumb_url = entries.get('media_thumbnail')
    if thumb_url:
        thumb_url = thumb_url[0].get('url')
        thumb = os.path.join(Config.DOWN_PATH, f"{title}.{str(thumb_url).split('.')[-1]}")
        if not os.path.exists(thumb):
            await pool.run_in_thread(wget.download)(thumb_url, thumb)
    if time:
        time = (parser.parse(time) + timedelta(hours=5, minutes=30)).replace(tzinfo=None)
    if entries.get('authors'):
        author = entries.get('authors')[0]['name'].split('/')[-1]
        author_link = entries.get('authors')[0]['href']
    out_str = f"""
**New post Found**

**Title:** `{title}`
**Author:** [{author}]({author_link})
**Last Updated:** `{time}`
"""
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="View Post Online", url=link)]])
    if thumb:
        args = {
            'caption': out_str,
            'parse_mode': "md",
            'reply_markup': markup if userge.has_bot else None
        }
    else:
        args = {
            'text': out_str,
            'disable_web_page_preview': True,
            'parse_mode': "md",
            'reply_markup': markup if userge.has_bot else None
        }
    for chat_id in RSS_CHAT_ID:
        args.update({'chat_id': chat_id})
        try:
            await send_rss_to_telegram(userge.bot, args, thumb)
        except (
            ChatWriteForbidden, ChannelPrivate, ChatIdInvalid,
            UserNotParticipant, UsergeBotNotFound
        ):
            out_str += f"\n\n[View Post Online]({link})"
            if 'caption' in args:
                args.update({'caption': out_str})
            else:
                args.update({'text': out_str})
            await send_rss_to_telegram(userge, args, thumb)


async def send_rss_to_telegram(client, args: dict, path: str = None):
    if path:
        if path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
            await client.send_photo(photo=path, **args)
        elif path.lower().endswith((".mkv", ".mp4", ".webm")):
            await client.send_video(video=path, **args)
        else:
            await client.send_document(document=path, **args)
    else:
        await client.send_message(**args)


@userge.on_cmd("addfeed", about={
    'header': "Add new Feed Url to get regular Updates from it.",
    'usage': "{tr}addfeed url"})
async def add_rss_feed(msg: Message):
    """ Add a New feed Url """
    if len(RSS_DICT) >= 10:
        return await msg.edit("`Sorry, but not allowing to add urls more than 10.`")
    if not msg.input_str:
        return await msg.edit("Check `.help addfeed`")
    try:
        rss = await _parse(msg.input_str)
    except IndexError:
        return await msg.edit("The link does not seem to be a RSS feed or is not supported")
    out_str = await add_new_feed(msg.input_str, rss.entries[0]['published'])
    await msg.edit(out_str, log=__name__)


@userge.on_cmd("delfeed", about={
    'header': "Delete a existing Feed Url from Database.",
    'flags': {'-all': 'Delete All Urls.'},
    'usage': "{tr}delfeed title"})
async def delete_rss_feed(msg: Message):
    """ Delete to a existing Feed Url """
    if msg.flags and '-all' in msg.flags:
        RSS_DICT.clear()
        PUBLISHED_DICT.clear()
        await RSS_COLLECTION.drop()
        return await msg.edit("`Deleted All feeds Successfully...`")
    if not msg.input_str:
        return await msg.edit("check `.help delfeed`")
    out_str = await delete_feed(msg.input_str)
    await msg.edit(out_str, log=__name__)


@userge.on_cmd("listrss", about={
    'header': "List all feed URLs that you Subscribed.",
    'usage': "{tr}listrss"})
async def list_rss_feed(msg: Message):
    """ List all Subscribed Feeds """
    out_str = ""
    for url, date in RSS_DICT.items():
        out_str += f"**FEED URL:** `{url}`"
        out_str += f"\n**LAST CHECKED:** `{date}`\n"
    if not out_str:
        out_str = "`No feed Url Found.`"
    await msg.edit(out_str)


@userge.add_task
async def rss_worker():
    global TASK_RUNNING  # pylint: disable=global-statement
    TASK_RUNNING = True
    if RSS_DICT and RSS_CHAT_ID[0] == Config.LOG_CHANNEL_ID:
        _LOG.info(
            "You have to add var for `RSS_CHAT_ID`, for Now i will send in LOG_CHANNEL")
    while RSS_DICT:
        for url in RSS_DICT:
            rss = await _parse(url)
            for entries in rss.entries[:4]:
                parsed_time = parser.parse(entries['published'])
                parsed_time = (parsed_time + timedelta(hours=5, minutes=30)).replace(tzinfo=None)
                if not parsed_time > PUBLISHED_DICT[url]:
                    datetime_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
                    RSS_DICT[url] = datetime_now
                    await RSS_COLLECTION.update_one(
                        {'url': url}, {"$set": {'last_updated': datetime_now}}, upsert=True
                    )
                    continue
                await send_new_post(entries)
                PUBLISHED_DICT[url] = parsed_time
                RSS_DICT[url] = parsed_time
                await RSS_COLLECTION.update_one(
                    {'url': url},
                    {"$set": {'last_updated': parsed_time, 'published': parsed_time}},
                    upsert=True
                )
            await asyncio.sleep(1)
        await asyncio.sleep(60)
    TASK_RUNNING = False


@pool.run_in_thread
def _parse(url: str) -> None:
    return feedparser.parse(url)
