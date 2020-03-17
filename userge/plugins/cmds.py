import io
import os
import sys
import asyncio
import traceback
from userge import userge, Config

log = userge.getLogger(__name__)


@userge.on_cmd("eval", about="run eval")
async def eval_(_, message):
    await message.edit("Processing ...")
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except:
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

    try:
        await aexec(cmd, userge, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"

    final_output = "**EVAL**: ```{}```\n\n**OUTPUT**:\n```{}``` \n".format(cmd, evaluation.strip())

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


async def aexec(code, userge, message):
    exec(
        f'async def __aexec(userge, message): ' +
        ''.join(f'\n {l}' for l in code.split('\n'))
    )
    return await locals()['__aexec'](userge, message)


@userge.on_cmd("exec", about="run exec")
async def exec_(_, message):
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except:
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


@userge.on_cmd("term", about="run terminal")
async def term_(_, message):
    await message.edit("Processing ...")
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except:
        await message.edit("__No Command Found!__")
        return

    reply_to_id = message.message_id

    if message.reply_to_message:
        reply_to_id = message.reply_to_message.message_id
    
    try:
        from os import geteuid
        uid = geteuid()
    except ImportError:
        uid = "This ain't it chief!"

    if cmd in ("config.env"):
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

        curruser = message.from_user.username \
            or message.from_user.first_name \
                or message.from_user.last_name \
                    or message.from_user.id

        if uid == 0:
            await message.edit("`" f"{curruser}:~# {cmd}" f"\n{OUTPUT}" "`")
        else:
            await message.edit("`" f"{curruser}:~$ {cmd}" f"\n{OUTPUT}" "`")