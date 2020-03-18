import os
from userge import userge

log = userge.getLogger(__name__)


@userge.on_cmd("whois", about="to get user details")
async def who_is(_, message):
    if " " in message.text:
        _, user_id = message.text.split(" ")

        try:
            user_id = int(user_id)
            from_user = await userge.get_users(user_id)

        except Exception as e:
            await message.edit(str(e))
            return

    elif message.reply_to_message:
        from_user = await userge.get_users(message.reply_to_message.from_user.id)

    else:
        await message.edit("no valid user_id / message specified")
        return

    if from_user is not None:
        message_out_str = ""

        message_out_str += f"<strong>USER INFO:</strong> \n"
        message_out_str += f"\n"
        message_out_str += f"<strong>First Name:</strong> {from_user.first_name}\n"
        message_out_str += f"<strong>Last Name:</strong> {from_user.last_name}\n"
        message_out_str += f"<strong>Username:</strong> @{from_user.username}\n"
        message_out_str += f"<strong>Data Centre ID:</strong> {from_user.dc_id}\n"
        message_out_str += f"<strong>Is Bot:</strong> {from_user.is_bot}\n"
        message_out_str += f"<strong>Is Restricted:</strong> {from_user.is_scam}\n"
        message_out_str += f"<strong>Is Verified by Telegram:</strong> {from_user.is_verified}\n"
        message_out_str += f"<strong>User ID:</strong> <code>{from_user.id}</code>\n"
        message_out_str += f"\n"
        message_out_str += f"<strong>Permanent Link To Profile:</strong> <a href='tg://user?id={from_user.id}'>{from_user.first_name}</a>"

        chat_photo = from_user.photo

        if chat_photo:
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

        else:
            message_out_str = "<b>No DP Found</b>\n\n" + message_out_str
            await message.edit(message_out_str, parse_mode="html")
