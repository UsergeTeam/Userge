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

        if " " in message.input_str:
            user_id, user_rank = message.input_str.split(" ")

            if user_id and user_rank:
                try:
                    await userge.promote_chat_member(chat_id, user_id)

                    await userge.set_administrator_title(chat_id, user_id, user_rank)

                    await message.edit("**👑 Promoted Successfully**")

                except Exception as e:
                    await message.err(
                        text=f"`something went wrong 🤔, do .help promote for more info` \n **ERROR** {str(e)}")

            else:
                try:
                    await userge.promote_chat_member(chat_id, user_id)

                    await message.edit("**👑 Promoted Successfully**")

                except Exception as e:
                    await message.err(
                        text=f"`something went wrong 🤔, do .help promote for more info` \n **ERROR** {str(e)}")

                return

        elif message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            user_rank = message.input_str

            if user_rank:

                try:
                    await userge.promote_chat_member(chat_id, user_id)

                    await userge.set_administrator_title(chat_id, user_id, user_rank)

                    await message.edit("**👑 Promoted Successfully**")

                except Exception as e:
                    await message.err(
                        text=f"`something went wrong 🤔, do .help promote for more info` \n **ERROR** {str(e)}")

            else:

                try:
                    await userge.promote_chat_member(chat_id, user_id)

                    await message.edit("**👑 Promoted Successfully**")

                except Exception as e:
                    await message.err(
                        text=f"`something went wrong 🤔, do .help promote for more info`\n **ERROR** {str(e)}")

                return

        else:
            await message.err(
                text="no valid user_id or message specified, do .help promote for more info")

    else:
        await message.err(
            text="`I don't have proper admin permission to do that ⚠`")
    return
