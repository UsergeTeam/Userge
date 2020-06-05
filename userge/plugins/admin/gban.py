""" setup gban """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved

import spamwatch

from userge import userge, Message, Config, get_collection, Filters

GBAN_USER_BASE = get_collection("GBAN_USER")
WHITELIST = get_collection("WHITELIST_USER")
GBAN_LOG = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)


async def me_is_admin(chat_id: int):
    check_user = await userge.get_chat_member(chat_id, (await userge.get_me()).id)
    if check_user.status == "creator":
        return True
    if check_user.status == "administrator" and check_user.can_restrict_members:
        return True
    return False


async def guadmin_check(chat_id, user_id) -> bool:
    check_status = await userge.get_chat_member(chat_id, user_id)
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
    """ ban a user globally """
    reason = ""
    chat_id = message.chat.id
    can_ban = await me_is_admin(chat_id)
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
    async for i in GBAN_USER_BASE.find({}):
        if i['user_id'] == user_id:
            await message.edit(
                "**#Already_GBanned**\n\nUser Already Exists in My Gban List.\n"
                "**Reason For GBan:** `{}`".format(i['reason']))
            return
    if user_id == (await userge.get_me()).id:
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


@userge.on_cmd("ungban", about={
    'header': "Globally Unban an User",
    'description': "Removes an user from your Gban List",
    'examples': "{tr}ungban [userid | reply]"})
async def ungban_user(message: Message):
    """ unban a user globally """
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


@userge.on_cmd("glist", about={
    'header': "Get a List of Gbanned Users",
    'description': "Get Up-to-date list of users Gbanned by you.",
    'examples': "Lol. Just type {tr}glist"})
async def list_gbanned(message: Message):
    """ vies gbanned users """
    msg = ''
    async for c in GBAN_USER_BASE.find({}):
        msg += ("**User** : " + str(c['firstname']) + "-> with **User ID** -> "
                + str(c['user_id']) + " is **GBanned for** : " + str(c['reason']) + "\n\n")
    await message.edit_or_send_as_file(
        f"**--Globally Banned Users List--**\n\n{msg}" if msg else "`glist empty!`")


@userge.on_cmd("whitelist", about={
    'header': "Whitelist a User",
    'description': "Use whitelist to add users to bypass API Bans",
    'useage': "{tr}whitelist [userid | reply to user]",
    'examples': "{tr}whitelist 5231147869"})
async def whitelist(message: Message):
    """ add user to whitelist """
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


@userge.on_cmd("rmwhite", about={
    'header': "Removes a User from Whitelist",
    'description': "Use it to remove users from WhiteList",
    'useage': "{tr}rmwhite [userid | reply to user]",
    'examples': "{tr}rmwhite 5231147869"})
async def rmwhitelist(message: Message):
    """ remove a user from whitelist """
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


@userge.on_cmd("listwhite", about={
    'header': "Get a List of Whitelisted Users",
    'description': "Get Up-to-date list of users WhiteListed by you.",
    'examples': "Lol. Just type {tr}listwhite"})
async def list_white(message: Message):
    """ list whitelist """
    msg = ''
    async for c in WHITELIST.find({}):
        msg += ("**User** : " + str(c['firstname']) + "-> with **User ID** -> " +
                str(c['user_id']) + "\n\n")
    await message.edit_or_send_as_file(
        f"**--Whitelisted Users List--**\n\n{msg}" if msg else "`whitelist empty!`")


@userge.on_filters(Filters.group & Filters.new_chat_members & ~Filters.me, group=1)
async def gban_at_entry(message: Message):
    """ handle gbans """
    chat_id = message.chat.id
    for user in message.new_chat_members:
        user_id = user.id
        first_name = user.first_name
        skip_user = False
        async for w in WHITELIST.find({}):
            if w['user_id'] == user_id:
                skip_user = True
                break
        if skip_user:
            continue
        if await me_is_admin(chat_id):
            async for c in GBAN_USER_BASE.find({}):
                if c['user_id'] == user_id:
                    reason = c['reason']
                    await userge.kick_chat_member(chat_id, user_id)
                    await message.reply(
                        r"\\**#Userge_Antispam**//"
                        "\n\n\nGlobally Banned User Detected in this Chat.\n\n"
                        f"**User:** [{first_name}](tg://user?id={user_id})\n"
                        f"**ID:** `{user_id}`\n**Reason:** `{reason}`\n\n"
                        "**Quick Action:** Banned.")
                    await GBAN_LOG.log(
                        r"\\**#Antispam_Log**//"
                        "\n\n**GBanned User $SPOTTED**\n"
                        f"**User:** [{first_name}](tg://user?id={user_id})\n"
                        f"**ID:** `{user_id}`\n**Reason:** {reason}\n**Quick Action:** "
                        f"Banned in {message.chat.title}")
                    break
            if Config.ANTISPAM_SENTRY and Config.SPAM_WATCH_API:
                intruder = spamwatch.Client(Config.SPAM_WATCH_API).get_ban(user_id)
                if intruder:
                    await userge.kick_chat_member(chat_id, user_id)
                    await message.reply(
                        r"\\**#Userge_Antispam**//"
                        "\n\n\nGlobally Banned User Detected in this Chat.\n\n"
                        "**$SENTRY SpamWatch Federation Ban**\n"
                        f"**User:** [{first_name}](tg://user?id={user_id})\n"
                        f"**ID:** `{user_id}`\n**Reason:** `{intruder.reason}`\n\n"
                        "**Quick Action:** Banned.")
                    await GBAN_LOG.log(
                        r"\\**#Antispam_Log**//"
                        "\n\n**GBanned User $SPOTTED**\n"
                        "**$SENRTY #SPAMWATCH_API BAN**"
                        f"\n**User:** [{first_name}](tg://user?id={user_id})\n"
                        f"**ID:** `{user_id}`\n**Reason:** `{intruder.reason}`\n"
                        f"**Quick Action:** Banned in {message.chat.title}\n\n"
                        f"$AUTOBAN #id{user_id}")
    message.continue_propagation()
