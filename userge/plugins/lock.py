from userge import userge
from pyrogram import ChatPermissions

@userge.on_cmd("lock",
    about="""__use this to get any user details__

**Usage:**

`Allows you to lock some common message types in the chat.`

[NOTE: Requires proper admin rights in the chat !!]

**Available types to Lock Messages:**

`all, msg, media, polls, invite, pin, info, other [animations, games, stickers, inline bots]`

**Example:**

    `.lock [all | type]`""")
async def lock_type(_, message):
    
    chat_id = message.chat.id
    if " " in message.text:
        _, lock_type = message.text.split(" ")

    msg = True
    media = True
    other = True
    polls = True
    info = True
    invite = True
    pin = True


    if lock_type == "all":
        perm = "Everything"
        await userge.set_chat_permissions(chat_id, ChatPermissions())
        await message.edit(f"`Locked {perm} for this Chat!`")
        return

    elif lock_type == "msg":
        msg = False
        perm = "messages"
    
    elif lock_type == "media":
        media = False
        perm = "audios, documents, photos, videos, video notes, voice notes"

    elif lock_type == "other":
        other = False
        perm = "animations, games, stickers, inline bots"

    elif lock_type == "polls":
        polls = False
        perm = "polls"

    elif lock_type == "info":
        info = False
        perm = "info"

    elif lock_type == "invite":
        invite = False
        perm = "invite"

    elif lock_type == "pin":
        pin = False
        perm = "pin"

    else:
        if not lock_type:
            await message.edit("`I Can't Lock Nothing! 🤦‍♂️`")
            return
        else:
            await message.edit(r"`Invalid Lock Type! ¯\_(ツ)_/¯`")
            return

    try:
        await userge.set_chat_permissions(
            chat_id,
            ChatPermissions(
                can_send_messages=msg,
                can_send_media_messages=media,
                can_send_other_messages=other,
                can_send_polls=polls,
                can_change_info=info,
                can_invite_users=invite,
                can_pin_messages=pin,
                )
            )
        await message.edit(f"`Locked {perm} for this chat!`")

    except Exception as e:
        await message.edit(f"`Do I have proper Admin rights for that?`\n**Error:** {str(e)}")
        return