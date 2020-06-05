# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved

import json

import requests
import spamwatch

from userge import userge, Message, Config, get_collection, Filters

GBAN_USER_BASE = get_collection("GBAN_USER")
WHITELIST = get_collection("WHITELIST_USER")
GBAN_LOG = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)


async def is_admin(message: Message, me_id):
    check_user = await userge.get_chat_member(message.chat.id, me_id)
    user_type = check_user.status
    if user_type == "member":
        return False
    if user_type == "administrator":
        rm_perm = check_user.can_restrict_members
        if rm_perm:
            return True
        return False
    return True


async def guadmin_check(chat_id, user_id) -> bool:
    check_status = await userge.get_chat_member(chat_id=chat_id, user_id=user_id)
    admin_strings = ["creator", "administrator"]
    if check_status.status not in admin_strings:
        return False
    return True


@userge.on_cmd("gban", about={
    'header': "Globally Ban A User",
    'description': "Adds User to your GBan List. "
                   "Bans a Globally Banned user if they join or message. "
                   "[NOTE: Works only in groups where you are admin.]",
    'examples': "{tr}gban [userid | reply] [reason for gban] (mandatory)"})
async def gban_user(message: Message):
    reason = ""
    chat_id = message.chat.id
    me = await userge.get_me()
    can_ban = await is_admin(message, me.id)

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        reason = message.input_str
    else:
        args = message.input_str.split(maxsplit=1)
        if len(args) == 2:
            user_id, reason = args
        elif len(args) == 1:
            user_id = args[0]
        else:
            await message.edit(
                "`no valid user_id or message specified,`"
                "`don't do .help gban for more info. "
                "Coz no one's gonna help ya`(｡ŏ_ŏ) ⚠", del_in=0)
            return

    get_mem = await userge.get_user_dict(user_id)
    firstname = get_mem['fname']
    user_id = get_mem['id']

    try:
        async for i in GBAN_USER_BASE.find({}):
            if i['user_id'] == user_id:
                await message.edit(
                    "**#Already_GBanned**\n\nUser Already Exists in My Gban List.\n"
                    "**Reason For GBan:** `{}`".format(i['reason']))
                return
        if user_id == me.id:
            await message.edit(r"LoL. Why would I GBan myself ¯\(°_o)/¯")
            return

        if user_id in Config.SUDO_USERS:
            await message.edit(
                "That user is in my Sudo List, Hence I can't ban him. \n\n"
                "**Tip:** Remove them from Sudo List and try again. (¬_¬)")
            return

        if reason:
            st = await message.edit(
                r"\\**#GBanned_User**//"
                f"\n\n**First Name:** [{firstname}](tg://user?id={user_id})\n"
                f"**User ID:** `{user_id}`\n     **Reason:** `{reason}`")
            # TODO: can we add something like "GBanned by {any_sudo_user_fname}"
        else:
            await message.edit(
                f"**#Aborted** \n\n**Gbanning** of [{firstname}](tg://user?id={user_id}) "
                "Aborted coz No reason of gban provided by banner")
            return

        await GBAN_USER_BASE.insert_one(
            {'firstname': firstname, 'user_id': user_id, 'reason': reason})

        if can_ban:
            gbanned_admeme = await guadmin_check(chat_id, user_id)
            if gbanned_admeme:
                await st.reply(
                    f"**#GBanned_user** is admin of {message.chat.title}\n\n"
                    "**Failed to Ban** but still they are GBanned")
            else:
                await userge.kick_chat_member(chat_id, user_id)

        LOG.info("G-Banned %s", str(user_id))

        await GBAN_LOG.log(
            r"\\**#Antispam_Log**//"
            f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`\n"
            f"**Chat:** {message.chat.title}\n"
            f"**Chat ID:** `{chat_id}`\n"
            f"**Reason:** `{reason}`\n\n$GBAN #id{user_id}"
        )
        try:
            if message.reply_to_message:
                await GBAN_LOG.fwd_msg(message.reply_to_message)
                await GBAN_LOG.log(f'$GBAN #prid{user_id} ⬆️')
                await message.reply_to_message.delete()
        except Exception:
            await message.reply("`I dont have message nuking rights! But still he got gbanned!`")
            return

    except Exception as e:
        LOG.error(str(e))
        await message.reply("Error: "+str(e))
        return


@userge.on_cmd("ungban", about={
    'header': "Globally Unban an User",
    'description': "Removes an user from your Gban List",
    'examples': "{tr}ungban [userid | reply]"})
async def ungban_user(message: Message):
    chat_id = message.chat.id

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        args = message.input_str.split(maxsplit=1)
        if len(args) == 2:
            user_id, _ = args
        elif len(args) == 1:
            user_id = args[0]
        else:
            await message.edit(
                "`no valid user_id or message specified,`"
                "`don't do .help gban for more info. "
                "Coz no one's gonna help ya`(｡ŏ_ŏ) ⚠", del_in=0)
            return

    get_mem = await userge.get_user_dict(user_id)
    firstname = get_mem['fname']
    user_id = get_mem['id']

    try:
        await GBAN_USER_BASE.delete_one({'firstname': firstname, 'user_id': user_id})
        await message.edit(
            r"\\**#UnGbanned_User**//"
            f"\n\n**First Name:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`")
        LOG.info("UnGbanned %s", str(user_id))
        await GBAN_LOG.log(
            r"\\**#Antispam_Log**//"
            f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`\n"
            f"**Chat:** {message.chat.title}\n"
            f"**Chat ID:** `{chat_id}`\n\n$UNGBAN #id{user_id}"
        )
    except Exception as e:
        LOG.exception('Received exception during ungban')
        await message.edit("Error: "+str(e))


@userge.on_cmd("glist", about={
    'header': "Get a List of Gbanned Users",
    'description': "Get Up-to-date list of users Gbanned by you.",
    'examples': "Lol. Just type {tr}glist"})
async def list_gbanned(message: Message):
    try:
        msg = ''
        async for c in GBAN_USER_BASE.find({}):
            msg += ("**User** : " + str(c['firstname']) + "-> with **User ID** -> "
                    + str(c['user_id']) + " is **GBanned for** : " + str(c['reason']) + "\n\n")
        await message.edit_or_send_as_file(
            f"**--Globally Banned Users List--**\n\n{msg}" if msg else "`glist empty!`")
    except Exception as e:
        LOG.exception('Received exception during gbannedList')
        await message.edit("Error: "+str(e))


@userge.on_cmd("whitelist", about={
    'header': "Whitelist a User",
    'description': "Use whitelist to add users to bypass API Bans",
    'useage': "{tr}whitelist [userid | reply to user]",
    'examples': "{tr}whitelist 5231147869"})
async def whitelist(message: Message):

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        args = message.input_str.split(maxsplit=1)
        if len(args) == 2:
            user_id, _ = args
        elif len(args) == 1:
            user_id = args[0]
        else:
            await message.edit(
                "`no valid user_id or message specified,`"
                "`don't do .help gban for more info. "
                "Coz no one's gonna help ya`(｡ŏ_ŏ) ⚠", del_in=0)
            return

    get_mem = await userge.get_user_dict(user_id)
    firstname = get_mem['fname']
    user_id = get_mem['id']

    try:
        await WHITELIST.insert_one({'firstname': firstname, 'user_id': user_id})
        await message.edit(
            r"\\**#Whitelisted_User**//"
            f"\n\n**First Name:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`")
        LOG.info("WhiteListed %s", str(user_id))
        await GBAN_LOG.log(
            r"\\**#Antispam_Log**//"
            f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`\n"
            f"**Chat:** {message.chat.title}\n"
            f"**Chat ID:** `{message.chat.id}`\n\n$WHITELISTED #id{user_id}"
        )
    except Exception as e:
        LOG.exception('Received exception during Whitelist')
        await message.edit("Error: " + str(e))


@userge.on_cmd("rmwhite", about={
    'header': "Removes a User from Whitelist",
    'description': "Use it to remove users from WhiteList",
    'useage': "{tr}rmwhite [userid | reply to user]",
    'examples': "{tr}rmwhite 5231147869"})
async def rmwhitelist(message: Message):

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        args = message.input_str.split(maxsplit=1)
        if len(args) == 2:
            user_id, _ = args
        elif len(args) == 1:
            user_id = args[0]
        else:
            await message.edit(
                "`no valid user_id or message specified,`"
                "`don't do .help gban for more info. "
                "Coz no one's gonna help ya`(｡ŏ_ŏ) ⚠", del_in=0)
            return

    get_mem = await userge.get_user_dict(user_id)
    firstname = get_mem['fname']
    user_id = get_mem['id']

    try:
        await WHITELIST.delete_one({'firstname': firstname, 'user_id': user_id})
        await message.edit(
            r"\\**#Removed_Whitelisted_User**//"
            f"\n\n**First Name:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`")
        LOG.info("WhiteListed %s", str(user_id))
        await GBAN_LOG.log(
            r"\\**#Antispam_Log**//"
            f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`\n"
            f"**Chat:** {message.chat.title}\n"
            f"**Chat ID:** `{message.chat.id}`\n\n$RMWHITELISTED #id{user_id}"
        )
    except Exception as e:
        LOG.exception('Received exception during remove whitelist')
        await message.edit("Error: " + str(e))


@userge.on_cmd("listwhite", about={
    'header': "Get a List of Whitelisted Users",
    'description': "Get Up-to-date list of users WhiteListed by you.",
    'examples': "Lol. Just type {tr}listwhite"})
async def list_white(message: Message):
    try:
        msg = ''
        async for c in WHITELIST.find({}):
            msg += ("**User** : " + str(c['firstname']) + "-> with **User ID** -> " +
                    str(c['user_id']) + "\n\n")
        await message.edit_or_send_as_file(
            f"**--Whitelisted Users List--**\n\n{msg}" if msg else "`whitelist empty!`")
    except Exception as e:
        LOG.exception('Received exception during WhiteList')
        await message.edit("Error: " + str(e))


@userge.on_filters(
    ~Filters.me & Filters.group & Filters.new_chat_members, group=1)
async def gban_at_entry(message: Message):
    try:
        if message.service:
            if message.new_chat_members:
                chat_id = message.chat.id
                user_id = message.new_chat_members[0].id
                firstname = message.new_chat_members[0].first_name
    except Exception:
        return  # Nu use to continue if u can't get id of user from message 🤔

    async for w in WHITELIST.find({}):
        if w['user_id'] == user_id:
            return

    try:
        async for c in GBAN_USER_BASE.find({}):
            if c['user_id'] == user_id:
                reason = c['reason']
                try:
                    if await guadmin_check(chat_id, user_id):
                        await userge.kick_chat_member(chat_id, user_id)
                        await message.reply(
                            r"\\**#Userge_Antispam**//"
                            "\n\n\nGlobally Banned User Detected in this Chat.\n\n"
                            f"**User:** [{firstname}](tg://user?id={user_id})\n"
                            f"**ID:** `{user_id}`\n**Reason:** `{reason}`\n\n"
                            "**Quick Action:** Banned.")
                        await GBAN_LOG.log(
                            r"\\**#Antispam_Log**//"
                            "\n\n**GBanned User $SPOTTED**\n"
                            f"**User:** [{firstname}](tg://user?id={user_id})\n"
                            f"**ID:** `{user_id}`\n**Reason:** {reason}\n**Quick Action:** "
                            "Banned in {message.chat.title}")
                except Exception:
                    break
    except Exception:
        pass

    if Config.ANTISPAM_SENTRY:
        try:
            if Config.SPAM_WATCH_API is not None:
                SENTRY = spamwatch.Client(Config.SPAM_WATCH_API)
                intruder = SENTRY.get_ban(user_id)
                if intruder and await guadmin_check(chat_id, user_id):
                    await userge.kick_chat_member(chat_id, user_id)
                    await message.reply(
                        r"\\**#Userge_Antispam**//"
                        "\n\n\nGlobally Banned User Detected in this Chat.\n\n"
                        "**$SENTRY SpamWatch Federation Ban**\n"
                        f"**User:** [{firstname}](tg://user?id={user_id})\n"
                        f"**ID:** `{user_id}`\n**Reason:** `{intruder.reason}`\n\n"
                        "**Quick Action:** Banned.")
                    await GBAN_LOG.log(
                        r"\\**#Antispam_Log**//"
                        "\n\n**GBanned User $SPOTTED**\n"
                        "**$SENRTY #SPAMWATCH_API BAN**"
                        f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
                        f"**ID:** `{user_id}`\n**Reason:** `{intruder.reason}`\n"
                        "**Quick Action:** Banned in {message.chat.title}\n\n$AUTOBAN #id{user_id}")
        except Exception:
            pass

        try:
            res = requests.get(f'https://combot.org/api/cas/check?user_id={user_id}')
            res_dict = json.loads(res.text)
            if res_dict['ok'] and await guadmin_check(chat_id, user_id):
                try:
                    reason = res_dict['result']['offenses']
                    await userge.kick_chat_member(chat_id, user_id)
                    await message.reply(
                        r"\\**#Userge_Antispam**//"
                        "\n\n\nGlobally Banned User Detected in this Chat.\n\n"
                        "**$SENTRY CAS Federation Ban**\n"
                        f"**User:** [{firstname}](tg://user?id={user_id})\n"
                        f"**ID:** `{user_id}`\n**Reason:** `{reason}`\n\n"
                        "**Quick Action:** Banned.")
                    await GBAN_LOG.log(
                        r"\\**#Antispam_Log**//"
                        "\n\n**GBanned User $SPOTTED**\n"
                        "**$SENRTY #CAS BAN**"
                        f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
                        f"**ID:** `{user_id}`\n**Reason:** `{reason}`\n**Quick Action:**"
                        " Banned in {message.chat.title}\n\n$AUTOBAN #id{user_id}")
                except Exception:
                    pass
        except Exception:
            pass
    message.continue_propagation()
