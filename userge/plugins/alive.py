from userge import userge

log = userge.getLogger(__name__)


@userge.on_cmd("alive", about="This command is just for fun XD")
async def alive(_, message: userge.MSG):
    await userge.send_sticker(message.chat.id, 'resources/sticker.webp')
    await message.delete()
    await userge.send_message(message.chat.id, "`USERGE is Up and Running`")
