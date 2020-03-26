import os
import wget
import speedtest
from userge import userge, Message
from userge.utils import humanbytes


@userge.on_cmd("speedtest", about="__test your server speed__")
async def speedtst(message: Message):
    await message.edit("`Running speed test . . .`")

    try:
        test = speedtest.Speedtest()
        test.get_best_server()

        await message.edit("`Performing download test . . .`")
        test.download()

        await message.edit("`Performing upload test . . .`")
        test.upload()

        test.results.share()
        result = test.results.dict()

    except Exception as e:
        await message.err(text=e)
        return

    path = wget.download(result['share'])

    output = f"""**--Started at {result['timestamp']}--

Client:

ISP: `{result['client']['isp']}`
Country: `{result['client']['country']}`

Server:

Name: `{result['server']['name']}`
Country: `{result['server']['country']}, {result['server']['cc']}`
Sponsor: `{result['server']['sponsor']}`
Latency: `{result['server']['latency']}`

Ping: `{result['ping']}`
Sent: `{await humanbytes(result['bytes_sent'])}`
Received: `{await humanbytes(result['bytes_received'])}`
Download: `{await humanbytes(result['download'])}/s`
Upload: `{await humanbytes(result['upload'])}/s`**"""

    await userge.send_photo(chat_id=message.chat.id,
                            photo=path,
                            caption=output)

    os.remove(path)
    await message.delete()
