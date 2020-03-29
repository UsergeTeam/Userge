from userge import userge, Message


@userge.on_cmd("promote", about="""\
__use this to promote group members__

**Usage:**

`Provides admin rights to the person in the chat.`

[NOTE: Requires proper admin rights in the chat!!!]


**Example:**

    `.promote [username | userid] [custom_rank]`""")

async def promote_usr(message: Message):
    """
    this function can promote members in tg group
    """
    chat_id = message.chat.id
    get_chat = await userge.get_chat_member(message.chat.id, message.from_user.id)
    promote_perm = get_chat.can_promote_members

    await message.edit("`Trying to Promote User.. Hang on!`")

    if promote_perm:

        user_id = message.input_str

        if user_id:
            try:
                await userge.promote_chat_member(chat_id, user_id)

                await message.edit("**👑 Promoted Successfully**", del_in=5)

            except Exception as e:
                await message.edit(
                    text=f"`something went wrong 🤔, do .help promote for more info` \n **ERROR** {str(e)}")

        else:

            user_id = message.reply_to_message.from_user.id

            try:
                await userge.promote_chat_member(chat_id, user_id)

                await message.edit("**👑 Promoted Successfully**", del_in=5)

            except Exception as e:
                await message.edit(
                    text=f"`something went wrong 🤔, do .help promote for more info` \n **ERROR** {str(e)}")

    else:
        await message.edit(
            text="`I don't have proper admin permission to do that ⚠`")
