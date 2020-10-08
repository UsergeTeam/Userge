"""Generate Memes"""


import asyncio
import json
import requests
from userge import userge, Message, Config
from userge.utils import rand_array


CHANNEL = userge.getCLogger(__name__)
URL = 'https://api.imgflip.com/caption_image'
PATH = 'resources/meme_data.txt'


@userge.on_cmd("gm", about={
    'header': "Get Customized memes",
    'flags': {
        '-m': "To choose a meme template"
    },
    'usage': "{tr}gm -m[number] text1 ; text2\n"
             "{tr}gm text1 ; text2",
    'examples': [
        "{tr}gm Hi ; Hello",
        "{tr}gm -m32 Hi ; Hello"],
    'Memes': "<a href='https://telegra.ph/Meme-Choices-10-01'><b>See MEME List</b></a>"})
async def gen_meme(message: Message):
    """ Memesss Generator """
    if not (Config.IMGFLIP_ID or Config.IMGFLIP_PASS):
        return await message.edit('First get `IMGFLIP_ID` = username and `IMGFLIP_PASS` = password via **https://imgflip.com/**')
    text = message.filtered_input_str
    if not text:
        return await message.err("No input found!", del_in=5)
    if ";" in text:
        text1, text2 = text.split(";", 1)
    else: 
        return await message.err("Invalid Input! Check help for more info!", del_in=5)
    view_data = json.load(open(PATH))
    if '-m' in message.flags:
        numb = int(message.flags['-m'])
        if numb in range(93):
            meme_choice = view_data[numb]
        else:
            return await message.err("Choose a number between (0 - 93) only !", del_in=5)
    else:
        meme_choice = eval(rand_array(view_data))
    choice_id = meme_choice['id']
    await message.edit(f"<code>Generating a meme for ...</code>\n{meme_choice['name']}")

    username = Config.IMGFLIP_ID
    password = Config.IMGFLIP_PASS
    reply = message.reply_to_message
    reply_id = reply.message_id if reply else None
    params = {
            'username': username,
            'password': password,
            'template_id': choice_id,
            'text0': text1,
            'text1': text2
            }
    response = requests.request('POST',URL,params=params).json()
    await asyncio.sleep(2)
    meme_image = response['data']['url']
    if not response['success']:
        return await message.err(f"<code>{response['error_message']}</code>", del_in=5)
    await message.delete()
    await message.client.send_photo(
        chat_id=message.chat.id,
        photo=meme_image,
        reply_to_message_id=reply_id
    )
    await CHANNEL.log("**name** : {}\n**image** : {}".format(meme_choice['name'], meme_image))
