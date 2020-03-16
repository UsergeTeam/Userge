import asyncio
import os
from userge import userge, Config

log = userge.getLogger(__name__)


@userge.on_cmd("exec", about="run exec")
async def exec_(_, message: userge.MSG):
    cmd = message.text.split(" ", maxsplit=1)[1]
    reply_to_id = message.message_id

    if message.reply_to_message:
        reply_to_id = message.reply_to_message.message_id

    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    e = stderr.decode() or "No Error"
    o = stdout.decode()

    if o:
        _o = o.split("\n")
        o = "`\n".join(_o)
    else:
        o = "**Tip**: \n`If you want to see the results of your code, I suggest printing them to stdout.`"

    OUTPUT = f"**QUERY:**\n__Command:__\n`{cmd}` \n__PID:__\n`{process.pid}`\n\n**stderr:** \n`{e}`\n**Output:**\n{o}"

    if len(OUTPUT) > Config.MAX_MESSAGE_LENGTH:
        with open("exec.text", "w+", encoding="utf8") as out_file:
            out_file.write(str(OUTPUT))

        await userge.send_document(
            chat_id=message.chat.id,
            document="exec.text",
            caption=cmd,
            disable_notification=True,
            reply_to_message_id=reply_to_id
        )

        os.remove("exec.text")
        await message.delete()

    else:
        await message.edit(OUTPUT)