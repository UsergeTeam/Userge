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
import pytz
import feedparser
from dateutil import parser

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChatWriteForbidden, ChannelPrivate, UserNotParticipant

from userge.utils.exceptions import UsergeBotNotFound
from userge import userge, Message, Config, logging, get_collection, pool

RSS_CHAT_ID = [int(x) for x in os.environ.get("RSS_CHAT_ID", "0").split()]
_LOG = logging.getLogger(__name__)

RSS_URLS = {}
RSS_COLLECTION = get_collection("RSS_DATA")


async def _init():
    async for url in RSS_COLLECTION.find():
        RSS_URLS[url['title']] = {
            'feed_url': url['feed_url'], 'last_post': url['last_post']
        }


async def add_new_feed(title: str, url: str, last_post: str) -> str:
    url_t = RSS_URLS.get(title)
    if url_t and url_t.get("feed_url") == url:
        out_str = "`This Url Feed is already in my database.`"
    else:
        out_str = f"""
#ADDED_NEW_FEED_URL

\t\t**TITLE:** `{title}`
\t\t**FEED_URL:** `{url}`
\t\t**LAST_POST:** `{last_post}`
"""
        RSS_URLS[title] = {'feed_url': url, 'last_post': last_post}
        await RSS_COLLECTION.update_one(
            {'title': title}, {"$set": {'feed_url': url, 'last_post': last_post}}
        )
    return out_str


async def delete_feed(title: str, url: str) -> str:
    url_t = RSS_URLS.get(title)
    if url_t and url_t.get("feed_url") == url:
        out_str = f"""
#DELETED_FEED_URL

\t\t**TITLE:** `{title}`
\t\t**FEED_URL:** `{url}`
"""
        del RSS_URLS[title]
        await RSS_COLLECTION.delete_one(
            {'title': title, 'feed_url': url}
        )
    else:
        out_str = "`This Url is not in my database.`"
    return out_str


async def send_new_post(entries):
    title = entries.get('title')
    link = entries.get('link')
    time = entries.get('time')
    thumb = None
    author = None
    author_link = None

    thumb_url = entries.get('media_thumbnail')
    if thumb_url:
        thumb = os.path.join(Config.DOWN_PATH, str(title).split('/')[-1])
        await pool.run_in_thread(wget.download)(thumb_url, thumb)
    if entries.get('time'):
        parse_time = parser.parse(entries)
        if parse_time.tzinfo is None:
            aware_date = pytz.utc.localize(parse_time)
            parse_time = aware_date.astimezone(pytz.timezone("India/Mumbai"))
        time = str(parse_time).split('+')[0][:-3]
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
            'file_id': thumb,
            'caption': out_str,
            'disable_web_page_preview': True,
            'parse_mode': "md",
            'reply_markup': markup
        }
    else:
        out_str += f"\n\n[View Post Online]({link})"
        args = {
            'text': out_str,
            'disable_web_page_preview': True,
            'parse_mode': "md",
            'reply_markup': markup
        }
    for chat_id in RSS_CHAT_ID:
        args.update({'chat_id': chat_id})
        try:
            await send_rss_to_telegram(userge.bot, args)
        except (ChatWriteForbidden, ChannelPrivate, UserNotParticipant, UsergeBotNotFound):
            await send_rss_to_telegram(userge, args)


async def send_rss_to_telegram(client, args: dict):
    path = None
    if args.get('file_id'):
        path = args.get('file_id')
    if path:
        del args['file_id']
        if path.lower().endswith(
            (".jpg", ".jpeg", ".png", ".bmp")
        ):
            args.update({'photo': path})
            await client.send_photo(**args)
        elif path.lower().endswith(
            (".mkv", ".mp4", ".webm")
        ):
            args.update({'video': path})
            await client.send_video(**args)
        else:
            args.update({'document': path})
            await client.send_document(**args)
    else:
        await client.send_message(**args)


@userge.on_cmd("addfeed", about={
    'header': "Add new Feed Url to get regular Updates from it.",
    'usage': "{tr}addfeed title | url"})
async def add_rss_feed(msg: Message):
    """ Add a New feed Url """
    if not (msg.input_str and '|' in msg.input_str):
        return await msg.edit("[Wrong syntax]\nCorrect syntax is addfeed title | feed_url")
    title, url = msg.input_str.split('|', maxsplit=1)
    if not url:
        return await msg.err("Without Feed Url how can I add feed?")
    title, url = title.strip(), url.strip()
    try:
        rss = await _parse(url)
    except IndexError:
        return await msg.edit("The link does not seem to be a RSS feed or is not supported")
    out_str = await add_new_feed(title, url, rss.entries[0]['link'])
    await msg.edit(out_str, log=__name__)


@userge.on_cmd("delfeed", about={
    'header': "Delete a existing Feed Url from Database.",
    'usage': "{tr}deletefeed title | url"})
async def delete_rss_feed(msg: Message):
    """ Delete to a existing Feed Url """
    if not (msg.input_str and '|' in msg.input_str):
        return await msg.edit("[Wrong syntax]\nCorrect syntax is delfeed title | feed_url")
    title, url = msg.input_str.split('|', maxsplit=1)
    if not url:
        return await msg.err("Without Feed Url how can I delete feed?")
    title, url = title.strip(), url.strip()
    out_str = await delete_feed(title, url)
    await msg.edit(out_str, log=__name__)


@userge.on_cmd("listrss", about={
    'header': "List all feed URLs that you Subscribed.",
    'usage': "{tr}listrss"})
async def list_rss_feed(msg: Message):
    """ List all Subscribed Feeds """
    out_str = ""
    for title, feed_urls in RSS_URLS.items():
        for url, last_post in feed_urls.items():
            out_str += f"\n**TITLE:** `{title}`"
            out_str += f"\n**FEED URL:** `{url}`"
            out_str += f"\n**LAST POST:** `{last_post}`\n\n"
    if not out_str:
        out_str = "`No feed Url Found.`"
    await msg.edit(out_str)


@userge.add_task
async def rss_worker():
    if not (RSS_URLS or RSS_CHAT_ID):
        if not RSS_CHAT_ID:
            _LOG.info("You should add var for `RSS_CHAT_ID`")
        return
    while True:
        for title, url in RSS_URLS.items():
            rss = await _parse(url['feed_url'])
            if url['last_post'] != rss.entries[0]['link']:
                RSS_URLS[title]['last_post'] = rss.entries[0]['link']
                await RSS_COLLECTION.update_one(
                    {'title': title, 'feed_url': url['feed_url']},
                    {"$set": {'last_post': rss.entries[0]['link']}}
                )
                await send_new_post(rss.entries[0])
        await asyncio.sleep(60)


@pool.run_in_thread
def _parse(url: str) -> None:
    return feedparser.parse(url)
