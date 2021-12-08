""" Bot Pm """

# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.
#
# Author (C) - @Krishna_Singhal (https://github.com/Krishna-Singhal)

import asyncio
import os
import re
import time
from typing import Optional, List, Dict

import wget
from pyrogram.errors import UserIsBlocked, FloodWait
from pyrogram.types import (
    Message as PyroMessage, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)

from userge import userge, Message, Config, filters, get_collection, pool
from userge.utils import SafeDict, time_formatter
from userge.utils.exceptions import StopConversation

CHANNEL = userge.getCLogger(__name__)

USERS = get_collection("BOT_PM_USERS")
HAVE_BLOCKED = get_collection("USER_BLOCKED_BOT_USERS")
BANNED_USERS = get_collection("BANNED_USERS")
U_ID_F_M_ID = get_collection("USER_ID_FROM_MESSAGE_ID")
STATS = get_collection("BOT_PM_STATS")
SAVED_SETTINGS = get_collection("CONFIGS")

BOT_PM: bool = False
IN_CONVO: bool = False
_USERS: List[int] = []
_HAVE_BLOCKED: List[int] = []
_BANNED_USERS: List[int] = []
_U_ID_F_M_ID: Dict[int, int] = {}
_STATS: Dict[str, int] = {"incoming": 0, "outgoing": 0}

START_TEXT = " Hello {mention}, you can contact me using this Bot."
START_MEDIA = os.environ.get("START_MEDIA")

botPmFilter = filters.create(lambda _, __, ___: BOT_PM)
bannedFilter = filters.create(lambda _, __, ___: ___.chat.id in _BANNED_USERS)


async def _init():
    global START_TEXT, BOT_PM  # pylint: disable=global-statement
    async for a in HAVE_BLOCKED.find():
        _HAVE_BLOCKED.append(a['user_id'])
    async for b in BANNED_USERS.find():
        _BANNED_USERS.append(b['user_id'])
    async for c in USERS.find():
        _USERS.append(c["user_id"])
    async for d in U_ID_F_M_ID.find():
        _U_ID_F_M_ID[d['msg_id']] = d['user_id']
    async for e in STATS.find():
        if e.get("_id") == "INCOMING_STATS":
            _STATS['incoming'] = e.get("data")
        if e.get("_id") == "OUTGOING_STATS":
            _STATS['outgoing'] = e.get("data")
    start_text = await SAVED_SETTINGS.find_one({"_id": "BOT_START_TEXT"})
    if start_text:
        START_TEXT = start_text.get("data")
    found = await SAVED_SETTINGS.find_one({"_id": "BOT_PM"})
    if found:
        BOT_PM = bool(found.get("data"))


@userge.on_cmd("botpm", about={
    'header': "Bot Pm handlers like Livegram Bot.",
    'description': "You can use this command to enable/disable Bot Pm.\n"
                   "You can see all the settings of your bot after enabling "
                   "bot pm and hit /start in your Bot DM.\n"
                   "Note: You have to us Bot mode or Dual mode if you want to enable Bot Pm.",
    'usage': "{tr}botpm"})
async def bot_pm(msg: Message):
    """ Toggle Bot Pm """
    global BOT_PM  # pylint: disable=global-statement
    if not userge.has_bot:
        return await msg.err("You have to us Bot mode or Dual mode if you want to enable Bot Pm.")
    BOT_PM = not BOT_PM
    await SAVED_SETTINGS.update_one(
        {"_id": "BOT_PM"}, {"$set": {"data": BOT_PM}}, upsert=True
    )
    await msg.edit(
        f"Bot Pm `{'Disabled ❌' if not BOT_PM else 'Enabled ✅'}` Successully.",
        del_in=5
    )


if userge.has_bot:
    userge_id = userge.id if userge.dual_mode else Config.OWNER_ID[0]
    bot = userge.bot

    @bot.on_message(
        ~bannedFilter & ~filters.edited & filters.private & filters.command("start"), group=1)
    async def start(_, msg: PyroMessage):
        user_id = msg.from_user.id
        user_dict = await bot.get_user_dict(user_id)
        text = START_TEXT.format_map(SafeDict(**user_dict))
        path = None
        if START_MEDIA:
            pattern = r"^https://telegra\.ph/file/\w+\.\w+$"
            if not re.match(pattern, START_MEDIA):
                await CHANNEL.log("Your `START_MEDIA` var is Invalid.")
            else:
                path = os.path.join(Config.DOWN_PATH, os.path.split(START_MEDIA)[1])
                if not os.path.exists(path):
                    await pool.run_in_thread(wget.download)(START_MEDIA, path)
        if user_id != userge_id:
            if user_id in _HAVE_BLOCKED:
                _HAVE_BLOCKED.remove(user_id)
                await HAVE_BLOCKED.delete_one({"user_id": user_id})
            if user_id not in _USERS:
                await bot.send_message(
                    userge_id,
                    f"📳 {msg.from_user.mention} just started me."
                )
                _USERS.append(user_id)
                await USERS.insert_one({"user_id": user_id})
            copy_ = "https://github.com/UsergeTeam/Userge/blob/master/LICENSE"
            markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(text="👥 UsergeTeam", url="https://github.com/UsergeTeam"),
                    InlineKeyboardButton(text="🧪 Repo", url=Config.UPSTREAM_REPO)
                ],
                [InlineKeyboardButton(text="🎖 GNU GPL v3.0", url=copy_)]
            ])
            await send_start_text(msg, text, path, markup)
            return
        text = "Hey, you can configure me here."
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Settings", callback_data="stngs")]])
        cmd = msg.command[1] if len(msg.command) > 1 else ''
        if cmd and ' ' not in msg.text:
            commands = userge.manager.enabled_commands
            key = Config.CMD_TRIGGER + cmd
            key_ = Config.SUDO_TRIGGER + cmd
            if cmd in commands:
                out_str = f"<code>{cmd}</code>\n\n{commands[cmd].about}"
            elif key in commands:
                out_str = f"<code>{key}</code>\n\n{commands[key].about}"
            elif key_ in commands:
                out_str = f"<code>{key_}</code>\n\n{commands[key_].about}"
            else:
                out_str = f"<i>No Command Found for</i>: <code>{cmd}</code>"
            return await msg.reply(out_str, parse_mode='html', disable_web_page_preview=True)
        await send_start_text(msg, text, path, markup)

    @bot.on_message(
        filters.user(userge_id) & filters.private & filters.command("settext"), group=1)
    async def set_text(_, msg: PyroMessage):
        global START_TEXT  # pylint: disable=global-statement
        text = msg.text.split(' ', maxsplit=1)[1] if ' ' in msg.text else ''
        replied = msg.reply_to_message
        if replied:
            text = replied.text or replied.caption
        if not text:
            await msg.reply("Text not found!")
        else:
            START_TEXT = text
            await SAVED_SETTINGS.update_one(
                {"_id": "BOT_START_TEXT"}, {"$set": {"data": text}}, upsert=True
            )
            await msg.reply("Custom Bot Pm text Saved Successfully.")

    @bot.on_message(filters.user(userge_id) & filters.private & filters.command("pmban"), group=1)
    async def pm_ban(_, msg: PyroMessage):
        replied = msg.reply_to_message
        user_id = msg.text.split(' ', maxsplit=1)[1] if ' ' in msg.text else ''
        if not (replied or user_id):
            await msg.reply("reply to user message or give id to Ban.")
        elif replied and replied.from_user.id == userge_id:
            await msg.reply("You are trying to Ban yourself!")
        else:
            if replied:
                if replied.forward_from:
                    user_id = replied.forward_from.id
                elif replied.message_id not in _U_ID_F_M_ID:
                    return await msg.reply("You can't reply old message of this user.")
                else:
                    user_id = _U_ID_F_M_ID.get(replied.message_id)
            else:
                # noinspection PyBroadException
                try:
                    user = await bot.get_users(int(user_id))
                except Exception:
                    return await msg.reply("Invalid User id.")
                user_id = user.id
            if user_id in _BANNED_USERS:
                return await msg.reply("You already banned this User.")
            if user_id in _USERS:
                _USERS.remove(user_id)
                await USERS.delete_one({"user_id": user_id})
            _BANNED_USERS.append(user_id)
            await BANNED_USERS.insert_one({"user_id": user_id})
            await msg.reply("User banned forever.")
            # noinspection PyBroadException
            try:
                await bot.send_message(user_id, "You have been Banned Forever.")
            except Exception:
                pass

    @bot.on_message(
        filters.user(userge_id) & filters.private & filters.command("pmunban"), group=1)
    async def pm_unban(_, msg: PyroMessage):
        replied = msg.reply_to_message
        user_id = msg.text.split(' ', maxsplit=1)[1] if ' ' in msg.text else ''
        if not (replied or user_id):
            await msg.reply("reply to user message or give id to UnBan.")
        elif replied and replied.from_user.id == userge_id:
            await msg.reply("You are trying to UnBan yourself!")
        else:
            if replied:
                if replied.forward_from:
                    user_id = replied.forward_from.id
                elif replied.message_id not in _U_ID_F_M_ID:
                    return await msg.reply("You can't reply old message of this user.")
                else:
                    user_id = _U_ID_F_M_ID.get(replied.message_id)
            else:
                # noinspection PyBroadException
                try:
                    user = await bot.get_users(int(user_id))
                except Exception:
                    return await msg.reply("Invalid User id.")
                user_id = user.id
            if user_id not in _BANNED_USERS:
                return await msg.reply("You haven't banned this User.")
            if user_id not in _USERS:
                _USERS.append(user_id)
                await USERS.insert_one({"user_id": user_id})
            _BANNED_USERS.remove(user_id)
            await BANNED_USERS.delete_one({"user_id": user_id})
            await msg.reply("User Unbanned.")
            # noinspection PyBroadException
            try:
                await bot.send_message(user_id, "You have been Unbanned.")
            except Exception:
                pass

    @bot.on_message(
        botPmFilter & ~bannedFilter & ~filters.edited & filters.private & filters.incoming, group=1
    )
    async def bot_pm_handler(_, msg: PyroMessage):
        if not hasattr(msg, '_client'):
            setattr(msg, '_client', _)
        user = msg.from_user
        if user.id == userge_id:
            await handle_reply(msg)
        else:
            await handle_incoming_message(msg)

    SETTINGS_TEXT = """ **Here are the Settings:** What do you want to do ?"""

    MISC_TEXT = "Click on the below button to change Bot Start Text or Start Media."

    SET_MEDIA_TEXT = """You can set Custom Start Media by Adding a Config Var named `START_MEDIA`.
Your var value should only contain telegraph link of any media.

After Adding a var, you can see your media when you start your Bot.
"""

    SET_CUSTOM_TEXT = """You can set Custom Start text which you will see when you start Bot by /settext command.
"""

    HELP_TEXT = """**Here are the available commands for Bot PM:**

/start - Start the bot
/settext [text | reply to text] - Set Custom Start Text
/pmban [user_id | reply to user] - Ban User from Doing Pms
/pmunban [user_id | reply to user] - UnBan Banned user
"""

    @bot.on_callback_query(
        filters.regex("startcq|stngs|bothelp|misc|setmedia|settext|broadcast|stats|en_dis_bot_pm")
    )
    async def cq_handler(_, cq: CallbackQuery):
        global BOT_PM, IN_CONVO  # pylint: disable=global-statement
        settings_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Broadcast", callback_data="broadcast"),
                    InlineKeyboardButton("Statistics", callback_data="stats")
                ],
                [
                    InlineKeyboardButton("Misc", callback_data="misc"),
                    InlineKeyboardButton("Help", callback_data="bothelp")
                ],
                [InlineKeyboardButton("Back", callback_data="startcq")]
            ]
        )
        if cq.data == "stngs":
            text = f"Bot Pm - {'Disabled ❌' if not BOT_PM else 'Enabled ✅'}"
            btn = [InlineKeyboardButton(text, callback_data="en_dis_bot_pm")]
            mp = settings_markup
            mp.inline_keyboard.insert(0, btn)
            await cq.edit_message_text(
                SETTINGS_TEXT,
                disable_web_page_preview=True,
                reply_markup=mp
            )
        elif cq.data == "en_dis_bot_pm":
            BOT_PM = not BOT_PM
            await SAVED_SETTINGS.update_one(
                {"_id": "BOT_PM"}, {"$set": {"data": BOT_PM}}, upsert=True
            )
            text = f"Bot Pm - {'Disabled ❌' if not BOT_PM else 'Enabled ✅'}"
            btn = [InlineKeyboardButton(text, callback_data=cq.data)]
            mp = settings_markup
            mp.inline_keyboard.insert(0, btn)
            await cq.edit_message_reply_markup(
                reply_markup=mp
            )
        elif cq.data == "bothelp":
            mp = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="stngs")]])
            await cq.edit_message_text(
                HELP_TEXT,
                disable_web_page_preview=True,
                reply_markup=mp
            )
        elif cq.data == "stats":
            mp = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="stngs")]])

            out_str = f"""**Statistics:**

**Users:**
**All Users:** `{len(_BANNED_USERS + _HAVE_BLOCKED + _USERS)}`
**Users:** `{len(_USERS)}`
**Banned Users:** `{len(_BANNED_USERS)}`
**Users who Blocked me:** `{len(_HAVE_BLOCKED)}`

**Messages:**
**All Messages:** `{_STATS["incoming"] + _STATS["outgoing"]}`
**Incoming:** `{_STATS["incoming"]}`
**Outgoing:** `{_STATS["outgoing"]}`
"""
            await cq.edit_message_text(
                out_str,
                disable_web_page_preview=True,
                reply_markup=mp
            )
        elif cq.data == "broadcast":
            await cq.message.delete()
            try:
                await broadcast(cq.message)
            except StopConversation as err:
                IN_CONVO = False
                if "message limit reached!" in str(err):
                    await cq.message.reply(
                        "You can only send 5 post message at once."
                    )
                else:
                    await cq.message.reply(
                        "**Broadcast process cancelled:** You didnt replied in 30 seconds."
                    )
        elif cq.data == "misc":
            mp = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Start Text", callback_data="settext"),
                        InlineKeyboardButton("Start Media", callback_data="setmedia")
                    ],
                    [InlineKeyboardButton("Back", callback_data="stngs")]
                ]
            )
            await cq.edit_message_text(
                MISC_TEXT,
                disable_web_page_preview=True,
                reply_markup=mp
            )
        elif cq.data == "setmedia":
            mp = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="misc")]])
            await cq.edit_message_text(
                SET_MEDIA_TEXT,
                disable_web_page_preview=True,
                reply_markup=mp
            )
        elif cq.data == "settext":
            mp = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="misc")]])
            await cq.edit_message_text(
                SET_CUSTOM_TEXT,
                disable_web_page_preview=True,
                reply_markup=mp
            )
        elif cq.data == "startcq":
            user_dict = await userge.get_user_dict(cq.from_user.id)
            mp = InlineKeyboardMarkup([[InlineKeyboardButton("Settings", callback_data="stngs")]])
            await cq.edit_message_text(
                START_TEXT.format_map(SafeDict(**user_dict)),
                disable_web_page_preview=True,
                reply_markup=mp
            )

    async def send_start_text(
        msg: PyroMessage, text: str, path: str, markup: Optional[InlineKeyboardMarkup] = None
    ):
        if not path:
            return await msg.reply(text, disable_web_page_preview=True, reply_markup=markup)
        if path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
            await bot.send_photo(
                chat_id=msg.chat.id,
                photo=path,
                caption=text,
                reply_markup=markup
            )
        elif path.lower().endswith((".mkv", ".mp4", ".webm")):
            await bot.send_video(
                chat_id=msg.chat.id,
                video=path,
                caption=text,
                reply_markup=markup
            )
        else:
            await bot.send_document(
                chat_id=msg.chat.id,
                document=path,
                caption=text,
                reply_markup=markup
            )

    async def increment_stats(incoming: bool):
        if incoming:
            _STATS["incoming"] += 1
            await STATS.update_one(
                {"_id": "INCOMING_STATS"}, {"$set": {"data": _STATS["incoming"]}}, upsert=True
            )
        else:
            _STATS["outgoing"] += 1
            await STATS.update_one(
                {"_id": "OUTGOING_STATS"}, {"$set": {"data": _STATS["outgoing"]}}, upsert=True
            )

    async def handle_incoming_message(msg: PyroMessage):
        user_id = msg.from_user.id
        if user_id in _HAVE_BLOCKED:
            _HAVE_BLOCKED.remove(user_id)
            await HAVE_BLOCKED.delete_one({"user_id": msg.from_user.id})
        if user_id not in _USERS:
            _USERS.append(user_id)
            await USERS.insert_one({"user_id": user_id})
        try:
            if msg.sticker:
                await bot.send_message(userge_id, f"{msg.from_user.mention} sent you a sticker.")
            m = await msg.forward(userge_id)
            if m.forward_from or m.forward_sender_name or m.forward_date:
                id_ = 0
                for a, b in _U_ID_F_M_ID.items():
                    if b == user_id:
                        id_ = a
                        break
                if id_:
                    del _U_ID_F_M_ID[id_]
                    await U_ID_F_M_ID.delete_one({"user_id": user_id})

                await U_ID_F_M_ID.insert_one(
                    {"user_id": user_id, "msg_id": m.message_id}
                )
                _U_ID_F_M_ID[m.message_id] = user_id
        except Exception as err:
            await CHANNEL.log(str(err), "INCOMING_HANDLER")
            await msg.reply("Your message is not received, try to send it again after some time.")
        else:
            await increment_stats(True)

    async def handle_reply(msg: PyroMessage):
        if IN_CONVO:
            return
        replied = msg.reply_to_message
        if not replied:
            await msg.reply("reply to user message to send reply.")
        elif replied.from_user.id == userge_id:
            await msg.reply("You are trying to reply yourself!")
        elif msg.forward_from or msg.forward_sender_name or msg.forward_date:
            await msg.reply("You can't forward someone else's messages.")
        else:
            if replied.forward_from:
                reply_id = replied.forward_from.id
            elif replied.message_id not in _U_ID_F_M_ID:
                return await msg.reply("You can't reply old message of this user.")
            else:
                reply_id = _U_ID_F_M_ID.get(replied.message_id)
            try:
                if msg.text:
                    await bot.send_message(reply_id, msg.text, disable_web_page_preview=True)
                else:
                    await msg.copy(reply_id)
            except UserIsBlocked:
                await msg.reply("Bot was Blocked by the user.")
                _USERS.remove(reply_id)
                _HAVE_BLOCKED.append(reply_id)
                await USERS.delete_one({"user_id": reply_id})
                await HAVE_BLOCKED.insert_one({"user_id": reply_id})
            except Exception as err:
                await msg.reply(str(err))
            else:
                await increment_stats(False)

    MESSAGE = f"""A broadcast post will be sent to {len(_USERS)} users.

Send one or multiple messages you want to include in the post.
It can be anything — a text, photo, video, even a sticker.

Type /cancel to cancel the operation.
"""

    NEXT_MESSAGE = "This message has been added to the post."
    PREVIEW_MESSAGE = "The post preview sent above."

    CONTINUE_MESSAGE = """{} You can continue to send messages. Type /done to send this broadcast post.

/preview — preview the broadcast post
/cancel - cancel the current operation
"""

    CONFIRM_TEXT = """Are you sure you want to send {} in broadcast post?

Type /send to confirm or /cancel to exit.
"""

    async def broadcast(msg: PyroMessage):
        global IN_CONVO  # pylint: disable=global-statement
        if len(_USERS) < 1:
            return await bot.send_message(msg.chat.id, "No one Started your bot. 🤭")
        IN_CONVO = True
        temp_msgs = []
        async with userge.bot.conversation(
                msg.chat.id, timeout=30, limit=7) as conv:  # 5 post msgs and 2 command msgs
            await conv.send_message(MESSAGE)
            filter_ = filters.create(lambda _, __, ___: filters.incoming & ~filters.edited)
            while True:
                response = await conv.get_response(filters=filter_)
                if response.text and response.text.startswith("/cancel"):
                    IN_CONVO = False
                    return await msg.reply("Broadcast process Cancelled.")
                if len(temp_msgs) >= 1 and response.text == "/done":
                    break
                if len(temp_msgs) >= 1 and response.text == "/preview":
                    conv._count -= 1
                    for i in temp_msgs:
                        if i.poll:
                            await conv.send_message("Poll Message.")
                            continue
                        await i.copy(conv.chat_id)
                    await conv.send_message(CONTINUE_MESSAGE.format(PREVIEW_MESSAGE))
                    continue
                if len(temp_msgs) >= 5:
                    raise StopConversation("message limit reached!")
                temp_msgs.append(response)
                await response.copy(conv.chat_id)
                await conv.send_message(CONTINUE_MESSAGE.format(NEXT_MESSAGE))
            confirm_text = CONFIRM_TEXT.format(len(temp_msgs))
            await conv.send_message(confirm_text)
            response = await conv.get_response(filters=filter_)
            while True:
                if response.text == "/send":
                    await send_broadcast_post(msg, temp_msgs)
                    IN_CONVO = False
                    return
                if response.text == "/cancel":
                    await conv.send_message("Broadcast process Cancelled.")
                    IN_CONVO = False
                    return
                conv._count -= 1
                await conv.send_message("Invalid Arguments!")
                await conv.send_message(confirm_text)
                response = await conv.get_response(filters=filter_)

    async def send_broadcast_post(msg: PyroMessage, to_send_messages: List[PyroMessage]):
        sending_text: str = f"🕒 Sending of the broadcast post to {len(_USERS)} users is started!"
        await bot.send_message(msg.chat.id, sending_text)
        blocked_users: List[int] = []
        count: int = 0
        success: int = 0
        sent: Optional[PyroMessage] = None
        start_time = time.time()
        for chat_id in _USERS:
            error: bool = False
            count += 1
            for message in to_send_messages:
                # noinspection PyBroadException
                try:
                    await message.copy(chat_id)
                except FloodWait as e:
                    await asyncio.sleep(e.x + 5)
                except UserIsBlocked:
                    blocked_users.append(chat_id)
                    error = True
                    break
                except Exception:
                    error = True
                    break
            if not error:
                success += 1
            if count % 5 == 0:
                percentage: str = f"{(count / len(_USERS)) * 100}%"
                out_str = f"Sent `{success}` from `{len(_USERS)}` (`{percentage}`)\n"
                out_str += f"**Failed:** `{count - success}`"
                try:
                    if not sent:
                        sent = await msg.reply(out_str)
                    else:
                        await sent.edit(out_str)
                except FloodWait as err:
                    await asyncio.sleep(err.x)
        if count % 5 != 0:
            percentage: str = f"{(count / len(_USERS)) * 100}%"
            out_str = f"Sent `{success}` from `{len(_USERS)}` (`{percentage}`)\n"
            out_str += f"**Failed:** `{count - success}`"
            try:
                if not sent:
                    await msg.reply(out_str)
                else:
                    await sent.edit(out_str)
            except FloodWait as err:
                await asyncio.sleep(err.x)
        end_time = time.time()
        if blocked_users:
            for user in blocked_users:
                _HAVE_BLOCKED.append(user)
                _USERS.remove(user)
                await HAVE_BLOCKED.insert_one({"user_id": user})
                await USERS.delete_one({"user_id": user})
        await msg.reply(
            "💥 Sending of the broadcast post is successfully completed "
            f"in  {time_formatter(end_time - start_time)}."
        )
