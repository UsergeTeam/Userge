""" setup auto pm message """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
from typing import Dict
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import BotInlineDisabled

from userge import userge, filters, Message, Config, get_collection
from userge.utils import SafeDict

CHANNEL = userge.getCLogger(__name__)
SAVED_SETTINGS = get_collection("CONFIGS")
ALLOWED_COLLECTION = get_collection("PM_PERMIT")

pmCounter: Dict[int, int] = {}
_IS_INLINE = True
allowAllFilter = filters.create(lambda _, __, ___: Config.ALLOW_ALL_PMS)
noPmMessage = bk_noPmMessage = ("Hello {fname} this is an automated message\n"
                                "Please wait until you get approved to direct message "
                                "And please dont spam until then ")
blocked_message = bk_blocked_message = "**You were automatically blocked**"


async def _init() -> None:
    global noPmMessage, blocked_message, _IS_INLINE  # pylint: disable=global-statement
    async for chat in ALLOWED_COLLECTION.find({"status": 'allowed'}):
        Config.ALLOWED_CHATS.add(chat.get("_id"))
    _pm = await SAVED_SETTINGS.find_one({'_id': 'PM GUARD STATUS'})
    if _pm:
        Config.ALLOW_ALL_PMS = bool(_pm.get('data'))
    i_pm = await SAVED_SETTINGS.find_one({'_id': 'INLINE_PM_PERMIT'})
    if i_pm:
        _IS_INLINE = bool(i_pm.get('data'))
    _pmMsg = await SAVED_SETTINGS.find_one({'_id': 'CUSTOM NOPM MESSAGE'})
    if _pmMsg:
        noPmMessage = _pmMsg.get('data')
    _blockPmMsg = await SAVED_SETTINGS.find_one({'_id': 'CUSTOM BLOCKPM MESSAGE'})
    if _blockPmMsg:
        blocked_message = _blockPmMsg.get('data')


@userge.on_cmd("allow", about={
    'header': "allows someone to contact",
    'description': "Ones someone is allowed, "
                   "Userge will not interfere or handle such private chats",
    'usage': "{tr}allow [username | userID]\nreply {tr}allow to a message, "
             "do {tr}allow in the private chat"}, allow_channels=False, allow_via_bot=False)
async def allow(message: Message):
    """ allows to pm """
    userid = await get_id(message)
    if userid:
        if userid in pmCounter:
            del pmCounter[userid]
        Config.ALLOWED_CHATS.add(userid)
        a = await ALLOWED_COLLECTION.update_one(
            {'_id': userid}, {"$set": {'status': 'allowed'}}, upsert=True)
        if a.matched_count:
            await message.edit("`Already approved to direct message`", del_in=3)
        else:
            await (await userge.get_users(userid)).unblock()
            await message.edit("`Approved to direct message`", del_in=3)
    else:
        await message.edit(
            "I need to reply to a user or provide the username/id or be in a private chat",
            del_in=3)


@userge.on_cmd("nopm", about={
    'header': "Activates guarding on inbox",
    'description': "Ones someone is allowed, "
                   "Userge will not interfere or handle such private chats",
    'usage': "{tr}nopm [username | userID]\nreply {tr}nopm to a message, "
             "do {tr}nopm in the private chat"}, allow_channels=False, allow_via_bot=False)
async def denyToPm(message: Message):
    """ disallows to pm """
    userid = await get_id(message)
    if userid:
        if userid in Config.ALLOWED_CHATS:
            Config.ALLOWED_CHATS.remove(userid)
        a = await ALLOWED_COLLECTION.delete_one({'_id': userid})
        if a.deleted_count:
            await message.edit("`Prohibitted to direct message`", del_in=3)
        else:
            await message.edit("`Nothing was changed`", del_in=3)
    else:
        await message.edit(
            "I need to reply to a user or provide the username/id or be in a private chat",
            del_in=3)


async def get_id(message: Message):
    userid = None
    if message.chat.type in ['private', 'bot']:
        userid = message.chat.id
    if message.reply_to_message:
        userid = message.reply_to_message.from_user.id
    if message.input_str:
        user = message.input_str.lstrip('@')
        try:
            userid = (await userge.get_users(user)).id
        except Exception as e:
            await message.err(str(e))
    return userid


@userge.on_cmd(
    "pmguard", about={
        'header': "Switchs the pm permiting module on",
        'description': "This is switched off in default. "
                       "You can switch pmguard On or Off with this command. "
                       "When you turn on this next time, "
                       "the previously allowed chats will be there !"},
    allow_channels=False)
async def pmguard(message: Message):
    """ enable or disable auto pm handler """
    global pmCounter  # pylint: disable=global-statement
    if Config.ALLOW_ALL_PMS:
        Config.ALLOW_ALL_PMS = False
        await message.edit("`PM_guard activated`", del_in=3, log=__name__)
    else:
        Config.ALLOW_ALL_PMS = True
        await message.edit("`PM_guard deactivated`", del_in=3, log=__name__)
        pmCounter.clear()
    await SAVED_SETTINGS.update_one(
        {'_id': 'PM GUARD STATUS'}, {"$set": {'data': Config.ALLOW_ALL_PMS}}, upsert=True)


@userge.on_cmd(
    "ipmguard", about={
        'header': "Switchs the Inline pm permiting module on",
        'description': "This is switched off in default.",
        'usage': "{tr}ipmguard"},
    allow_channels=False)
async def ipmguard(message: Message):
    """ enable or disable inline pmpermit """
    global _IS_INLINE  # pylint: disable=global-statement
    if _IS_INLINE:
        _IS_INLINE = False
        await message.edit("`Inline PM_guard deactivated`", del_in=3, log=__name__)
    else:
        _IS_INLINE = True
        await message.edit("`Inline PM_guard activated`", del_in=3, log=__name__)
    await SAVED_SETTINGS.update_one(
        {'_id': 'INLINE_PM_PERMIT'}, {"$set": {'data': _IS_INLINE}}, upsert=True)


@userge.on_cmd("setpmmsg", about={
    'header': "Sets the reply message",
    'description': "You can change the default message which userge gives on un-invited PMs",
    'flags': {'-r': "reset to default"},
    'options': {
        '{fname}': "add first name",
        '{lname}': "add last name",
        '{flname}': "add full name",
        '{uname}': "username",
        '{chat}': "chat name",
        '{mention}': "mention user"}}, allow_channels=False)
async def set_custom_nopm_message(message: Message):
    """ setup custom pm message """
    global noPmMessage  # pylint: disable=global-statement
    if '-r' in message.flags:
        await message.edit('`Custom NOpm message reset`', del_in=3, log=True)
        noPmMessage = bk_noPmMessage
        await SAVED_SETTINGS.find_one_and_delete({'_id': 'CUSTOM NOPM MESSAGE'})
    else:
        string = message.input_or_reply_raw
        if string:
            await message.edit('`Custom NOpm message saved`', del_in=3, log=True)
            noPmMessage = string
            await SAVED_SETTINGS.update_one(
                {'_id': 'CUSTOM NOPM MESSAGE'}, {"$set": {'data': string}}, upsert=True)
        else:
            await message.err("invalid input!")


@userge.on_cmd("ipmmsg", about={
    'header': "Set inline pm msg for Inline pmpermit",
    'usage': "{tr}ipmmsg [text | reply to text msg]"}, allow_channels=False)
async def change_inline_message(message: Message):
    """ set inline pm message """
    string = message.input_or_reply_raw
    if string:
        await message.edit('`Custom inline pm message saved`', del_in=3, log=True)
        await SAVED_SETTINGS.update_one(
            {'_id': 'CUSTOM_INLINE_PM_MESSAGE'}, {"$set": {'data': string}}, upsert=True)
    else:
        await message.err("invalid input!")


@userge.on_cmd("setbpmmsg", about={
    'header': "Sets the block message",
    'description': "You can change the default blockPm message "
                   "which userge gives on un-invited PMs",
    'flags': {'-r': "reset to default"},
    'options': {
        '{fname}': "add first name",
        '{lname}': "add last name",
        '{flname}': "add full name",
        '{uname}': "username",
        '{chat}': "chat name",
        '{mention}': "mention user"}}, allow_channels=False)
async def set_custom_blockpm_message(message: Message):
    """ setup custom blockpm message """
    global blocked_message  # pylint: disable=global-statement
    if '-r' in message.flags:
        await message.edit('`Custom BLOCKpm message reset`', del_in=3, log=True)
        blocked_message = bk_blocked_message
        await SAVED_SETTINGS.find_one_and_delete({'_id': 'CUSTOM BLOCKPM MESSAGE'})
    else:
        string = message.input_or_reply_raw
        if string:
            await message.edit('`Custom BLOCKpm message saved`', del_in=3, log=True)
            blocked_message = string
            await SAVED_SETTINGS.update_one(
                {'_id': 'CUSTOM BLOCKPM MESSAGE'}, {"$set": {'data': string}}, upsert=True)
        else:
            await message.err("invalid input!")


@userge.on_cmd(
    "vpmmsg", about={
        'header': "Displays the reply message for uninvited PMs"},
    allow_channels=False)
async def view_current_noPM_msg(message: Message):
    """ view current pm message """
    await message.edit(f"--current PM message--\n\n{noPmMessage}")


@userge.on_cmd(
    "vbpmmsg", about={
        'header': "Displays the reply message for blocked PMs"},
    allow_channels=False)
async def view_current_blockPM_msg(message: Message):
    """ view current block pm message """
    await message.edit(f"--current blockPM message--\n\n{blocked_message}")


@userge.on_filters(~allowAllFilter & filters.incoming & filters.private & ~filters.bot
                   & ~filters.me & ~filters.service & ~Config.ALLOWED_CHATS, allow_via_bot=False)
async def uninvitedPmHandler(message: Message):
    """ pm message handler """
    user_dict = await userge.get_user_dict(message.from_user.id)
    user_dict.update({'chat': message.chat.title if message.chat.title else "this group"})
    if message.from_user.is_verified:
        return
    if message.from_user.id in pmCounter:
        if pmCounter[message.from_user.id] > 3:
            del pmCounter[message.from_user.id]
            await message.reply(
                blocked_message.format_map(SafeDict(**user_dict))
            )
            await message.from_user.block()
            await asyncio.sleep(1)
            await CHANNEL.log(
                f"#BLOCKED\n{user_dict['mention']} has been blocked due to spamming in pm !! ")
        else:
            pmCounter[message.from_user.id] += 1
            await message.reply(
                f"You have {pmCounter[message.from_user.id]} out of 4 **Warnings**\n"
                "Please wait until you get approved to pm !", del_in=5)
    else:
        pmCounter.update({message.from_user.id: 1})
        if userge.has_bot and _IS_INLINE:
            try:
                bot_username = (await userge.bot.get_me()).username
                k = await userge.get_inline_bot_results(bot_username, "pmpermit")
                await userge.send_inline_bot_result(
                    message.chat.id, query_id=k.query_id,
                    result_id=k.results[2].id, hide_via=True
                )
            except (IndexError, BotInlineDisabled):
                await message.reply(
                    noPmMessage.format_map(SafeDict(**user_dict)) + '\n`- Protected by userge`')
        else:
            await message.reply(
                noPmMessage.format_map(SafeDict(**user_dict)) + '\n`- Protected by userge`')
        await asyncio.sleep(1)
        await CHANNEL.log(f"#NEW_MESSAGE\n{user_dict['mention']} has messaged you")


@userge.on_filters(~allowAllFilter & filters.outgoing & ~filters.edited
                   & filters.private & ~Config.ALLOWED_CHATS, allow_via_bot=False)
async def outgoing_auto_approve(message: Message):
    """ outgoing handler """
    userID = message.chat.id
    if userID in pmCounter:
        del pmCounter[userID]
    Config.ALLOWED_CHATS.add(userID)
    await ALLOWED_COLLECTION.update_one(
        {'_id': userID}, {"$set": {'status': 'allowed'}}, upsert=True)
    user_dict = await userge.get_user_dict(userID)
    await CHANNEL.log(f"**#AUTO_APPROVED**\n{user_dict['mention']}")

if userge.has_bot:
    @userge.bot.on_callback_query(filters.regex(pattern=r"pm_allow\((.+?)\)"))
    async def pm_callback_allow(_, c_q: CallbackQuery):
        owner = await userge.get_me()
        if c_q.from_user.id == owner.id:
            userID = int(c_q.matches[0].group(1))
            await userge.unblock_user(userID)
            user = await userge.get_users(userID)
            if userID in Config.ALLOWED_CHATS:
                await c_q.edit_message_text(
                    f"{user.mention} already allowed to Direct Messages.")
            else:
                await c_q.edit_message_text(
                    f"{user.mention} allowed to Direct Messages.")
                await userge.send_message(
                    userID, f"{owner.mention} `approved you to Direct Messages.`")
                if userID in pmCounter:
                    del pmCounter[userID]
                Config.ALLOWED_CHATS.add(userID)
                await ALLOWED_COLLECTION.update_one(
                    {'_id': userID}, {"$set": {'status': 'allowed'}}, upsert=True)
        else:
            await c_q.answer(f"Only {owner.first_name} have access to Allow.")

    @userge.bot.on_callback_query(filters.regex(pattern=r"pm_block\((.+?)\)"))
    async def pm_callback_block(_, c_q: CallbackQuery):
        owner = await userge.get_me()
        if c_q.from_user.id == owner.id:
            userID = int(c_q.matches[0].group(1))
            user_dict = await userge.get_user_dict(userID)
            await userge.send_message(
                userID, blocked_message.format_map(SafeDict(**user_dict)))
            await userge.block_user(userID)
            if userID in pmCounter:
                del pmCounter[userID]
            if userID in Config.ALLOWED_CHATS:
                Config.ALLOWED_CHATS.remove(userID)
            k = await ALLOWED_COLLECTION.delete_one({'_id': userID})
            user = await userge.get_users(userID)
            if k.deleted_count:
                await c_q.edit_message_text(
                    f"{user.mention} `Prohibitted to direct message`")
            else:
                await c_q.edit_message_text(
                    f"{user.mention} `already Prohibitted to direct messages.`")
        else:
            await c_q.answer(f"Only {owner.first_name} have access to Block.")

    @userge.bot.on_callback_query(filters.regex(pattern=r"^pm_spam$"))
    async def pm_spam_callback(_, c_q: CallbackQuery):
        owner = await userge.get_me()
        if c_q.from_user.id == owner.id:
            await c_q.answer("Sorry, you can't click by yourself")
        else:
            del pmCounter[c_q.from_user.id]
            user_dict = await userge.get_user_dict(c_q.from_user.id)
            await c_q.edit_message_text(
                blocked_message.format_map(SafeDict(**user_dict)))
            await userge.block_user(c_q.from_user.id)
            await asyncio.sleep(1)
            await CHANNEL.log(
                f"#BLOCKED\n{c_q.from_user.mention} has been blocked due to spamming in pm !! ")

    @userge.bot.on_callback_query(filters.regex(pattern=r"^pm_contact$"))
    async def pm_contact_callback(_, c_q: CallbackQuery):
        owner = await userge.get_me()
        if c_q.from_user.id == owner.id:
            await c_q.answer("Sorry, you can't click by yourself")
        else:
            user_dict = await userge.get_user_dict(c_q.from_user.id)
            await c_q.edit_message_text(
                noPmMessage.format_map(SafeDict(**user_dict)) + '\n`- Protected by userge`')
            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Allow", callback_data=f"pm_allow({c_q.from_user.id})"),
                        InlineKeyboardButton(
                            text="Block", callback_data=f"pm_block({c_q.from_user.id})")
                    ]
                ]
            )
            await userge.bot.send_message(
                owner.id,
                f"{c_q.from_user.mention} wanna contact to you.",
                reply_markup=buttons
            )
