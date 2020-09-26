""" run shell or python command(s) """

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
import keyword
import traceback
from getpass import getuser
from os import geteuid

from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified

from userge import userge, Message, Config
from userge.utils import runcmd


@userge.on_cmd("eval", about={
    'header': "run python code line | lines",
    'flags': {'-s': "silent mode (hide STDIN)"},
    'usage': "{tr}eval [flag] [code lines]",
    'examples': [
        "{tr}eval print('Userge')", "{tr}eval -s print('Userge')",
        "{tr}eval 5 + 6", "{tr}eval -s 5 + 6"]}, allow_channels=False)
async def eval_(message: Message):
    """ run python code """
    cmd = await init_func(message)
    if cmd is None:
        return
    silent_mode = False
    if cmd.startswith('-s'):
        silent_mode = True
        cmd = cmd[2:].strip()
    if not cmd:
        await message.err("Unable to Parse Input!")
        return
    await message.edit("`Executing eval ...`", parse_mode='md')
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    ret_val, stdout, stderr, exc = None, None, None, None

    async def aexec(code):
        head = "async def __aexec(userge, message):\n "
        if '\n' in code:
            rest_code = '\n '.join(line for line in code.split('\n'))
        elif any(True for k_ in keyword.kwlist
                 if k_ not in ('True', 'False', 'None') and code.startswith(f"{k_} ")):
            rest_code = f"\n {code}"
        else:
            rest_code = f"\n return {code}"
        exec(head + rest_code)  # nosec pylint: disable=W0122
        return await locals()['__aexec'](userge, message)
    try:
        ret_val = await aexec(cmd)
    except Exception:  # pylint: disable=broad-except
        exc = traceback.format_exc().strip()
    stdout = redirected_output.getvalue().strip()
    stderr = redirected_error.getvalue().strip()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = exc or stderr or stdout or ret_val
    output = ""
    if not silent_mode:
        output += f"**>** ```{cmd}```\n\n"
    if evaluation:
        output += f"**>>** ```{evaluation}```"
    if output:
        await message.edit_or_send_as_file(text=output,
                                           parse_mode='md',
                                           filename="eval.txt",
                                           caption=cmd)
    else:
        await message.delete()


@userge.on_cmd("exec", about={
    'header': "run commands in exec",
    'usage': "{tr}exec [commands]",
    'examples': "{tr}exec echo \"Userge\""}, allow_channels=False)
async def exec_(message: Message):
    """ run commands in exec """
    cmd = await init_func(message)
    if cmd is None:
        return
    await message.edit("`Executing exec ...`")
    try:
        out, err, ret, pid = await runcmd(cmd)
    except Exception as t_e:  # pylint: disable=broad-except
        await message.err(t_e)
        return
    out = out or "no output"
    err = err or "no error"
    out = "\n".join(out.split("\n"))
    output = f"**EXEC**:\n\n\
__Command:__\n`{cmd}`\n__PID:__\n`{pid}`\n__RETURN:__\n`{ret}`\n\n\
**stderr:**\n`{err}`\n\n**stdout:**\n``{out}`` "
    await message.edit_or_send_as_file(text=output,
                                       parse_mode='md',
                                       filename="exec.txt",
                                       caption=cmd)


@userge.on_cmd("term", about={
    'header': "run commands in shell (terminal)",
    'usage': "{tr}term [commands]",
    'examples': "{tr}term echo \"Userge\""}, allow_channels=False)
async def term_(message: Message):
    """ run commands in shell (terminal with live update) """
    cmd = await init_func(message)
    if cmd is None:
        return
    await message.edit("`Executing terminal ...`")
    try:
        t_obj = await Term.execute(cmd)  # type: Term
    except Exception as t_e:  # pylint: disable=broad-except
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
        if count >= Config.EDIT_SLEEP_TIMEOUT * 2:
            count = 0
            out_data = f"<pre>{output}{t_obj.read_line}</pre>"
            await message.try_to_edit(out_data, parse_mode='html')
    out_data = f"<pre>{output}{t_obj.get_output}</pre>"
    try:
        await message.edit_or_send_as_file(
            out_data, parse_mode='html', filename="term.txt", caption=cmd)
    except MessageNotModified:
        pass


async def init_func(message: Message):
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
