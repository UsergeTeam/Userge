""" a instagram post downloader plugin for @theUserge. """
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import re
import shutil
import asyncio

from natsort import natsorted
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from pyrogram.types import InputMediaPhoto, InputMediaVideo
from pyrogram.errors import FloodWait
from instaloader import (
    Instaloader, Post, Profile, NodeIterator,
    TwoFactorAuthRequiredException, InvalidArgumentException, BadCredentialsException,
    ConnectionException, LoginRequiredException
)

from userge import userge, pool, Message, Config
from userge.plugins.misc.upload import get_thumb, remove_thumb


# some helpers
def get_caption(post: Post) -> str:
    """ adds link to profile for tagged users """
    caption = post.caption
    replace = '<a href="https://instagram.com/{}/">{}</a>'
    for mention in post.caption_mentions:
        men = '@' + mention
        val = replace.format(mention, men)
        caption = caption.replace(men, val)
    header = f'♥️`{post.likes}`  💬`{post.comments}`'
    if post.is_video:
        header += f'  👀`{post.video_view_count}`'
    caption = header + '\n\n' + (caption or '')
    return caption


async def upload_to_tg(message: Message, dirname: str, post: Post) -> None:  # pylint: disable=R0912
    """ uploads downloaded post from local to telegram servers """
    pto = (".jpg", ".jpeg", ".png", ".bmp")
    vdo = (".mkv", ".mp4", ".webm")
    paths = []
    if post.typename == 'GraphSidecar':
        # upload media group
        captioned = False
        media = []
        for path in natsorted(os.listdir(dirname)):
            ab_path = dirname + '/' + path
            paths.append(ab_path)
            if str(path).endswith(pto):
                if captioned:
                    media.append(InputMediaPhoto(media=ab_path))
                else:
                    media.append(InputMediaPhoto(media=ab_path, caption=get_caption(post)[:1023]))
                    captioned = True
            elif str(path).endswith(vdo):
                if captioned:
                    media.append(InputMediaVideo(media=ab_path))
                else:
                    media.append(InputMediaVideo(media=ab_path, caption=get_caption(post)[:1023]))
                    captioned = True
        if media:
            await message.client.send_media_group(message.chat.id, media)
            await message.client.send_media_group(Config.LOG_CHANNEL_ID, media)

    if post.typename == 'GraphImage':
        # upload a photo
        for path in natsorted(os.listdir(dirname)):
            if str(path).endswith(pto):
                ab_path = dirname + '/' + path
                paths.append(ab_path)
                await message.client.send_photo(
                    message.chat.id,
                    ab_path,
                    caption=get_caption(post)[:1023])
                await message.client.send_photo(
                    Config.LOG_CHANNEL_ID,
                    ab_path,
                    caption=get_caption(post)[:1023])

    if post.typename == 'GraphVideo':
        # upload a video
        for path in natsorted(os.listdir(dirname)):
            if str(path).endswith(vdo):
                ab_path = dirname + '/' + path
                paths.append(ab_path)
                thumb = await get_thumb(ab_path)
                duration = 0
                metadata = extractMetadata(createParser(ab_path))
                if metadata and metadata.has("duration"):
                    duration = metadata.get("duration").seconds

                await message.client.send_video(
                    chat_id=message.chat.id,
                    video=ab_path,
                    duration=duration,
                    thumb=thumb,
                    caption=get_caption(post)[:1023])
                await message.client.send_video(
                    chat_id=Config.LOG_CHANNEL_ID,
                    video=ab_path,
                    duration=duration,
                    thumb=thumb,
                    caption=get_caption(post)[:1023])
                await remove_thumb(thumb)
    for del_p in paths:
        if os.path.lexists(del_p):
            os.remove(del_p)


# run some process in threads?
@pool.run_in_thread
def download_post(client: Instaloader, post: Post) -> bool:
    """ Downloads content and returns True """
    client.download_post(post, post.owner_username)
    return True


@pool.run_in_thread
def get_post(client: Instaloader, shortcode: str) -> Post:
    """ returns a post object """
    return Post.from_shortcode(client.context, shortcode)


@pool.run_in_thread
def get_profile(client: Instaloader, username: str) -> Profile:
    """ returns profile """
    return Profile.from_username(client.context, username)


@pool.run_in_thread
def get_profile_posts(profile: Profile) -> NodeIterator[Post]:
    """ returns a iterable Post object """
    return profile.get_posts()


# pylint: disable=R0914, R0912, R0915, R0911
@userge.on_cmd("postdl", about={
    'header': "Instagram Post Downloader",
    'description': "Download a post of a instagram user by passing post link or download all posts "
                   "by passing username of instagram user (<code>requires flag</code>)",
    'flags': {'-u': "use this to define a batch download of post",
              '-l': "limit the number of posts to be downloaded"},
    'usage': "{tr}postdl [flag] [link|username]",
    'examples': [
        "{tr}postdl https://www.instagram.com/××××××××××/",
        "{tr}postdl https://www.instagram.com/×××××××××/igshid=×××××/",
        "{tr}postdl -u [username]",
        "{tr}postdl -u instagram"]})
async def _insta_post_downloader(message: Message):
    """ download instagram post """
    await message.edit('`Setting up Configs. Please don\'t flood.`')
    dirname = 'instadl_{target}'
    filename = '{target}\'s_post'
    insta = Instaloader(
        dirname_pattern=dirname,
        filename_pattern=filename,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )
    if Config.INSTA_ID and Config.INSTA_PASS:
        # try login
        try:
            insta.load_session_from_file(Config.INSTA_ID)
            await message.edit('`Logged in with current Session`')
        except FileNotFoundError:
            await message.edit('`Login required. Trying to login`')
            try:
                insta.login(Config.INSTA_ID, Config.INSTA_PASS)
            except InvalidArgumentException:
                await message.err('Provided `INSTA_ID` is incorrect')
                return
            except BadCredentialsException:
                await message.err('Provided `INSTA_PASS` is incorrect')
                return
            except ConnectionException:
                await message.err('Instagram refused to connect. Try again later or never'
                                  ' (your choice)😒')
                return
            # This is a nightmare.
            except TwoFactorAuthRequiredException:
                # Send a promt for 2FA code in saved messages
                chat_type = 'Saved Messages' if message.from_user.is_self else 'Private Message'
                text = ('[<b>2 Factor Authentication Detected</b>]\n'
                        f'I have sent a message to {chat_type}. '
                        'Please continue there and send your 2FA code.')
                await message.edit(text)
                for _ in range(4):
                    # initial convo with the user who sent message in pm.
                    # if user is_self convo in saved messages
                    # else in pm of sudo user
                    async with userge.conversation(message.from_user.id) as asker:
                        asked = await asker.send_message('Please reply me with your 2FA code `int`')
                        response = await asker.get_response(mark_read=True)
                        if not (response.reply_to_message and response.reply_to_message.is_self):
                            # I said reply me.
                            continue
                        code = response.text
                        if not (code.isdigit() and len(code) == 6):
                            # the six digit code
                            # What else it has always been a six digit code.
                            continue
                        try:
                            insta.two_factor_login(code)
                            break
                        except BadCredentialsException as b_c_e:
                            await asked.err(b_c_e)
                        except InvalidArgumentException:
                            await asked.edit('`No pending Login Found`')
                            return
            else:
                try:
                    insta.save_session_to_file()
                except LoginRequiredException:
                    await message.err('Failed to save session file, probably due to invalid login.')
                    await asyncio.sleep(5)
    else:
        await message.edit('Login Credentials not found.\n`[NOTE]`: '
                           '**You may not be able to download private contents or so**')
        await asyncio.sleep(2)

    p = r'^https:\/\/www\.instagram\.com\/(p|tv|reel)\/([A-Za-z0-9\-_]*)\/(\?igshid=[a-zA-Z0-9]*)?$'
    match = re.search(p, message.input_str)

    if '-u' in message.flags:
        username = message.filtered_input_str
        sent = await message.edit(f'`Fetching all posts of {username}`')
        profile = await get_profile(insta, username)
        limit = int(message.flags.get("-l", 0))
        count = 0
        for post in await get_profile_posts(profile):
            count += 1
            if message.process_is_canceled:
                await sent.edit("Post Download Interrupted...")
                await asyncio.sleep(5)
                break
            try:
                await download_post(insta, post)
                await upload_to_tg(message, dirname.format(target=post.owner_username), post)
            except FloodWait as f_w:
                await asyncio.sleep(f_w.x + 10)
                await upload_to_tg(message, dirname.format(target=post.owner_username), post)
            except (KeyError, LoginRequiredException):
                await message.err('Private Content Login Required')
                return
            finally:
                shutil.rmtree(dirname.format(target=post.owner_username), ignore_errors=True)
            if limit > 0 and count == limit:
                break
        await sent.delete()
    elif match:
        dtypes = {
            'p': 'POST',
            'tv': 'IGTV',
            'reel': 'REELS'
        }
        d_t = dtypes.get(match.group(1))
        if not d_t:
            await message.err('Unsupported Format')
            return
        sent = await message.edit(f'`Fetching {d_t} Content.`')
        shortcode = match.group(2)
        post = await get_post(insta, shortcode)
        try:
            await download_post(insta, post)
            await upload_to_tg(message, dirname.format(target=post.owner_username), post)
        except (KeyError, LoginRequiredException):
            await message.err("Post is private. Login and try again")
            return
        except FloodWait as f_w:
            await asyncio.sleep(f_w.x + 5)
            await upload_to_tg(message, dirname.format(target=post.owner_username), post)
        finally:
            shutil.rmtree(dirname.format(target=post.owner_username), ignore_errors=True)
        await sent.delete()
    else:
        await message.err('`Invalid Input`')
