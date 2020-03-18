import io
import os
import sys
import asyncio
import traceback
from getpass import getuser
from userge import userge, Config

log = userge.getLogger(__name__)


@userge.on_cmd("eval", about="run eval")
async def eval_(_, message):
    await message.edit("Processing ...")

    try:
        cmd = message.text.split(" ", maxsplit=1)[1]

    except IndexError:
        await message.edit("__No Command Found!__")
        return

    reply_to_id = message.message_id
    if message.reply_to_message:
        reply_to_id = message.reply_to_message.message_id

    old_stderr = sys.stderr
    old_stdout = sys.stdout

    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()

    stdout, stderr, exc = None, None, None

    async def aexec(code, userge, message):
        exec(
            "async def __aexec(userge, message):\n " + '\n '.join(line for line in code.split('\n'))
        )
        return await locals()['__aexec'](userge, message)

    try:
        await aexec(cmd, userge, message)
        
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()

    sys.stdout = old_stdout
    sys.stderr = old_stderr

    if exc:
        evaluation = exc

    elif stderr:
        evaluation = stderr

    elif stdout:
        evaluation = stdout

    else:
        evaluation = "Success"

    final_output = "**EVAL**:\n```{}```\n\n**OUTPUT**:\n```{}```".format(cmd, evaluation.strip())

    if len(final_output) > Config.MAX_MESSAGE_LENGTH:
        with open("eval.text", "w+", encoding="utf8") as out_file:
            out_file.write(str(final_output))

        await userge.send_document(
            chat_id=message.chat.id,
            document="eval.text",
            caption=cmd,
            disable_notification=True,
            reply_to_message_id=reply_to_id
        )

        os.remove("eval.text")
        await message.delete()

    else:
        await message.edit(final_output)


@userge.on_cmd("exec", about="run exec")
async def exec_(_, message):
    await message.edit("Processing ...")

    try:
        cmd = message.text.split(" ", maxsplit=1)[1]

    except IndexError:
        await message.edit("__No Command Found!__")
        return

    reply_to_id = message.message_id
    if message.reply_to_message:
        reply_to_id = message.reply_to_message.message_id

    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    err = stderr.decode() or "no error"
    out = stdout.decode() or "no output"

    out = "\n".join(out.split("\n"))

    OUTPUT = f"**EXEC**:\n\n__Command:__\n`{cmd}`\n__PID:__\n`{process.pid}`\n\n**stderr:**\n`{err}`\n\n**stdout:**\n``{out}`` "

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


@userge.on_cmd("term", about="run terminal")
async def term_(_, message):
    await message.edit("Processing ...")

    try:
        cmd = message.text.split(" ", maxsplit=1)[1]

    except IndexError:
        await message.edit("__No Command Found!__")
        return

    reply_to_id = message.message_id
    if message.reply_to_message:
        reply_to_id = message.reply_to_message.message_id

    if "config.env" in cmd:
        await message.edit("`That's a dangerous operation! Not Permitted!`")
        return

    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    OUTPUT = str(stdout.decode().strip()) + str(stderr.decode().strip())

    if len(OUTPUT) > Config.MAX_MESSAGE_LENGTH:
        with open("term.text", "w+", encoding="utf8") as out_file:
            out_file.write(str(OUTPUT))

        await userge.send_document(
            chat_id=message.chat.id,
            document="term.text",
            caption=cmd,
            disable_notification=True,
            reply_to_message_id=reply_to_id
        )

        os.remove("term.text")
        await message.delete()

    else:
        try:
            from os import geteuid
            uid = geteuid()

        except ImportError:
            uid = 1

        curruser = getuser()

        if uid == 0:
            await message.edit("`" f"{curruser}:~# {cmd}" f"\n{OUTPUT}" "`")
            
        else:
            await message.edit("`" f"{curruser}:~$ {cmd}" f"\n{OUTPUT}" "`")