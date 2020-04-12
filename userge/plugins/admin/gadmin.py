# Copyright (C) 2020 by UsergeTeam@Telegram, < https://t.me/theUserge >.
#
# This file is part of < https://github.com/uaudith/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from userge import userge, Message

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd("promote", about="""\
__use this to promote group members__

**Usage:**

`Provides admin rights to the person in the supergroup.`

[NOTE: Requires proper admin rights in the chat!!!]


**Example:**

    `.promote [username | userid] or [reply to user]`""")

async def promote_usr(message: Message):
    """
    this function can promote members in tg group
    """
    chat_id = message.chat.id
    check_admin = await userge.get_chat_member(chat_id, message.from_user.id)
    get_group = await userge.get_chat(chat_id)
    promote_perm = check_admin.can_promote_members

    await message.edit("`Trying to Promote User.. Hang on!`")

    if promote_perm:

        if message.input_str:

            user_id = message.input_str
            get_mem = await userge.get_chat_member(chat_id, user_id)

            try:
                await userge.promote_chat_member(chat_id, user_id,
                                                 can_change_info=True,
                                                 can_delete_messages=True,
                                                 can_restrict_members=True,
                                                 can_invite_users=True,
                                                 can_pin_messages=True)

                await message.edit("**👑 Promoted Successfully**", del_in=5)

                await CHANNEL.log(
                    f"#PROMOTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id})\n"
                    f"CHAT: {get_group.title} (`{chat_id}`)")

            except:
                await message.edit(
                    text="`something went wrong 🤔, do .help promote for more info`", del_in=5)

        else:

            user_id = message.reply_to_message.from_user.id
            get_mem = await userge.get_chat_member(chat_id, user_id)

            try:
                await userge.promote_chat_member(chat_id, user_id,
                                                 can_change_info=True,
                                                 can_delete_messages=True,
                                                 can_restrict_members=True,
                                                 can_invite_users=True,
                                                 can_pin_messages=True)

                await message.edit("**👑 Promoted Successfully**", del_in=5)

                await CHANNEL.log(
                    f"#PROMOTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id})\n"
                    f"CHAT: {get_group.title} (`{chat_id}`)")

            except:
                await message.edit(
                    text="`something went wrong 🤔, do .help promote for more info`", del_in=5)

    else:
        await message.edit(
            text="`Looks like i don't have proper admin permission to do that ⚠`", del_in=5)


@userge.on_cmd("demote", about="""\
__use this to demote group members__

**Usage:**

`Remove admin rights from admin in the supergroup.`

[NOTE: Requires proper admin rights in the chat!!!]


**Example:**

    `.demote [username | userid] or [reply to user]`""")

async def demote_usr(message: Message):
    """
    this function can demote members in tg group
    """
    chat_id = message.chat.id
    check_admin = await userge.get_chat_member(chat_id, message.from_user.id)
    get_group = await userge.get_chat(chat_id)
    demote_perm = check_admin.can_promote_members

    await message.edit("`Trying to Demote User.. Hang on!`")

    if demote_perm:

        if message.input_str:

            user_id = message.input_str
            get_mem = await userge.get_chat_member(chat_id, user_id)

            try:
                await userge.promote_chat_member(chat_id, user_id,
                                                 can_change_info=False,
                                                 can_delete_messages=False,
                                                 can_restrict_members=False,
                                                 can_invite_users=False,
                                                 can_pin_messages=False)

                await message.edit("**🛡 Demoted Successfully**", del_in=5)
                await CHANNEL.log(
                    f"#DEMOTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id})\n"
                    f"CHAT: {get_group.title} (`{chat_id}`)")

            except:
                await message.edit(
                    text="`something went wrong 🤔, do .help demoted for more info`", del_in=5)

        else:

            user_id = message.reply_to_message.from_user.id
            get_mem = await userge.get_chat_member(chat_id, user_id)

            try:
                await userge.promote_chat_member(chat_id, user_id,
                                                 can_change_info=False,
                                                 can_delete_messages=False,
                                                 can_restrict_members=False,
                                                 can_invite_users=False,
                                                 can_pin_messages=False)

                await message.edit("**🛡 Demoted Successfully**", del_in=5)
                await CHANNEL.log(
                    f"#DEMOTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id})\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except:
                await message.edit(
                    text="`something went wrong 🤔, do .help demote for more info`", del_in=5)

    else:
        await message.edit(
            text="`Looks like i don't have proper admin permission to do that ⚠`", del_in=5)
