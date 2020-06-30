""" run shell or python command """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import io
import sys
import asyncio
import traceback
from getpass import getuser
from os import geteuid

from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified

from userge import userge, Message
from userge.utils import runcmd


@userge.on_cmd("eval", about={
    'header': "run python code line | lines",
    'usage': "{tr}eval [code lines]",
    'examples': "{tr}eval print('Userge')"}, allow_channels=False)
async def eval_(message: Message):
    """ run python code """
    cmd = await init_func(message)
    if cmd is None:
        return
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    async def aexec(code):
        exec("async def __aexec(userge, message):\n "
             + '\n '.join(line for line in code.split('\n')))
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
    'usage': "{tr}exec [commands]",
    'examples': "{tr}exec echo \"Userge\""}, allow_channels=False)
async def exec_(message: Message):
    """ run shell command """
    cmd = await init_func(message)
    if cmd is None:
        return
    try:
        out, err, ret, pid = await runcmd(cmd)
    except Exception as t_e:
        await message.err(t_e)
        return
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
    'usage': "{tr}term [commands]",
    'examples': "{tr}term echo \"Userge\""}, allow_channels=False)
async def term_(message: Message):
    """ run shell command (live update) """
    cmd = await init_func(message)
    if cmd is None:
        return
    try:
        t_obj = await Term.execute(cmd)  # type: Term
    except Exception as t_e:
        await message.err(t_e)
        return
    curruser = getuser()
    try:
        uid = geteuid()
    except ImportError:
        uid = 1
    if uid == 0:
        output = f"{curruser}:~# {cmd}\n"
    else:
        output = f"{curruser}:~$ {cmd}\n"
    count = 0
    while not t_obj.finished:
        count += 1
        if message.process_is_canceled:
            t_obj.cancel()
            await message.reply("`process canceled!`")
            return
        await asyncio.sleep(0.5)
        if count >= 10:
            count = 0
            out_data = f"<code>{output}{t_obj.read_line}</code>"
            await message.try_to_edit(out_data, parse_mode='html')
    out_data = f"<code>{output}{t_obj.get_output}</code>"
    try:
        await message.edit_or_send_as_file(
            out_data, parse_mode='html', filename="term.txt", caption=cmd)
    except MessageNotModified:
        pass


async def init_func(message: Message):
    await message.edit("`Processing ...`")
    cmd = message.input_str
    if not cmd:
        await message.err("No Command Found!")
        return None
    if "config.env" in cmd:
        await message.err("That's a dangerous operation! Not Permitted!")
        return None
    return cmd


class Term:
    """ live update term class """
    def __init__(self, process: asyncio.subprocess.Process) -> None:
        self._process = process
        self._stdout = b''
        self._stderr = b''
        self._stdout_line = b''
        self._stderr_line = b''
        self._finished = False

    def cancel(self) -> None:
        self._process.kill()

    @property
    def finished(self) -> bool:
        return self._finished

    @property
    def read_line(self) -> str:
        return (self._stdout_line + self._stderr_line).decode('utf-8').strip()

    @property
    def get_output(self) -> str:
        return (self._stdout + self._stderr).decode('utf-8').strip()

    async def _read_stdout(self) -> None:
        while True:
            line = await self._process.stdout.readline()
            if line:
                self._stdout_line = line
                self._stdout += line
            else:
                break

    async def _read_stderr(self) -> None:
        while True:
            line = await self._process.stderr.readline()
            if line:
                self._stderr_line = line
                self._stderr += line
            else:
                break

    async def worker(self) -> None:
        await asyncio.wait([self._read_stdout(), self._read_stderr()])
        await self._process.wait()
        self._finished = True

    @classmethod
    async def execute(cls, cmd: str) -> 'Term':
        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        t_obj = cls(process)
        asyncio.get_event_loop().create_task(t_obj.worker())
        return t_obj
