#https://github.com/UsergeTeam/Userge
from pyrogram import filters
from userge import userge, Message

@userge.on_cmd("channel", about={
    'header': "Creates a channel",
    'description': "Creates a channel with a name"},
    allow_channels=False, allow_bots=False)
async def create_ch(message:Message):
    try:
      args = message.text.split(None, 1)
      title = args[1]
      await userge.create_channel(title, 'nice')
      await message.edit(f"`successfully made a new channel {title}`")
    except Exception as e:
       message.edit("something went wrong")
       print(e)
