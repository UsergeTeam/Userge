import os
from userge import userge

log = userge.getLogger(__name__)


@userge.on_cmd("whois", about="to get user details")
async def who_is(_, message: userge.MSG):
    from_user = None
    if " " in message.text:
        recvd_command, user_id = message.text.split(" ")
        try:
            user_id = int(user_id)
            from_user = await userge.get_users(user_id)
        except Exception as e:
            await message.edit(str(e))
            return
    elif message.reply_to_message:
        from_user = message.reply_to_message.from_user
    else:
        await message.edit("no valid user_id / message specified")
        return
    if from_user is not None:
        message_out_str = ""
        message_out_str += f"ID: `{from_user.id}`\n"
        message_out_str += f"First Name: <a href='tg://user?id={from_user.id}'>{from_user.first_name}</a>\n"
        message_out_str += f"Last Name: {from_user.last_name}"
        chat_photo = from_user.photo
        local_user_photo = await userge.download_media(
            message=chat_photo.big_file_id
        )
        await message.reply_photo(
            photo=local_user_photo,
            quote=True,
            caption=message_out_str,
            parse_mode="html",
            # ttl_seconds=,
            disable_notification=True
        )
        os.remove(local_user_photo)
        await message.delete()