from pyrogram import ChatPermissions
from userge import userge

@userge.on_cmd("lock",
    about="""__use this to lock group permissions__

**Usage:**

`Allows you to lock some common message types in the chat.`

[NOTE: Requires proper admin rights in the chat!!!]

**Available types to Lock Messages:**

`all, msg, media, polls, invite, pin, info, other [animations, games, stickers, inline bots]`

**Example:**

    `.lock [all | type]`""")

async def lock_perm(_, message):
    """
    this function can lock chat permissions from tg group
    """
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
        perm = "all permission"
        await userge.set_chat_permissions(chat_id, ChatPermissions())
        await message.edit(f"`🔐 Locked {perm} from this Chat!`")

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
        else:
            await message.edit(r"`Invalid Lock Type! ¯\_(ツ)_/¯`")

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
        await message.edit(f"`🔐 Locked {perm} for this chat!`")

    except:
        await message.edit("`Do I have proper Admin rights for that ⚠`")
        return

@userge.on_cmd("unlock",
    about="""__use this to unlock group permissions__

**Usage:**

`Allows you to unlock all message types in the chat.`

[NOTE: Requires proper admin rights in the chat!!!]

**Example:**

    `.unlock all`""")

async def unlock_perm(_, message):
    """
    this function can unlock chat permissions from tg group
    """
    chat_id = message.chat.id
    if " " in message.text:
        _, unlock_type = message.text.split(" ")

    if unlock_type == "all":
        uperm = "all permissions"
        await userge.set_chat_permissions(
            chat_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_add_web_page_previews=True,
            )
        )
        await message.edit(f"`🔓 Unlocked {uperm} for this Chat!`")

    else:
        await message.edit("""
        'something went wrong! do .help unlock to see how this module works'
        """)
        return
