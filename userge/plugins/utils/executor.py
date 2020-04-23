# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import io
import sys
import traceback
from getpass import getuser
from os import geteuid
from userge import userge, Message
from userge.utils import runcmd


@userge.on_cmd("eval", about={
    'header': "run python code line | lines",
    'usage': ".eval [code lines]",
    'examples': ".eval print('Userge')"})
async def eval_(message: Message):
    cmd = await init_func(message)

    if cmd is None:
        return

    old_stderr = sys.stderr
    old_stdout = sys.stdout

    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()

    stdout, stderr, exc = None, None, None

    async def aexec(code):
        exec("async def __aexec(userge, message):\n " + \
                '\n '.join(line for line in code.split('\n')))

        return await locals()['__aexec'](userge, message)

    try:
        await aexec(cmd)

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

    output = "**EVAL**:\n```{}```\n\n\
**OUTPUT**:\n```{}```".format(cmd, evaluation.strip())

    await message.edit_or_send_as_file(text=output,
                                       filename="eval.txt",
                                       caption=cmd)


@userge.on_cmd("exec", about={
    'header': "run shell commands",
    'usage': ".exec [commands]",
    'examples': ".exec echo \"Userge\""})
async def exec_(message: Message):
    cmd = await init_func(message)

    if cmd is None:
        return

    out, err, ret, pid = await runcmd(cmd)

    out = out or "no output"
    err = err or "no error"

    out = "\n".join(out.split("\n"))

    output = f"**EXEC**:\n\n\
__Command:__\n`{cmd}`\n__PID:__\n`{pid}`\n__RETURN:__\n`{ret}`\n\n\
**stderr:**\n`{err}`\n\n**stdout:**\n``{out}`` "

    await message.edit_or_send_as_file(text=output,
                                       filename="exec.txt",
                                       caption=cmd)


@userge.on_cmd("term", about={
    'header': "run terminal commands",
    'usage': ".term [commands]",
    'examples': ".term echo \"Userge\""})
async def term_(message: Message):
    cmd = await init_func(message)

    if cmd is None:
        return

    out, err, _, _ = await runcmd(cmd)
    curruser = getuser()

    try:
        uid = geteuid()

    except ImportError:
        uid = 1

    if uid == 0:
        output = f"`{curruser}:~# {cmd}\n{str(out) + str(err)}`"

    else:
        output = f"`{curruser}:~$ {cmd}\n{str(out) + str(err)}`"

    await message.edit_or_send_as_file(text=output,
                                       filename="term.txt",
                                       caption=cmd)


async def init_func(message: Message):
    await message.edit("Processing ...")
    cmd = message.input_str

    if not cmd:
        await message.err(text="No Command Found!")
        return None

    if "config.env" in cmd:
        await message.err(text="That's a dangerous operation! Not Permitted!")
        return None

    return cmd
