""" run shell or python command(s) """

# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import io
import sys
import asyncio
import keyword
import re
import shlex
import threading
import traceback
from contextlib import contextmanager
from enum import Enum
from getpass import getuser
from os import geteuid
from typing import Awaitable, Any, Callable, Dict, Optional, Tuple, Iterable

from pyrogram.types.messages_and_media.message import Str

from userge import userge, Message, Config, pool
from userge.utils import runcmd

CHANNEL = userge.getCLogger()


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
        await message.err(str(t_e))
        return

    output = f"**EXEC**:\n\n\
__Command:__\n`{cmd}`\n__PID:__\n`{pid}`\n__RETURN:__\n`{ret}`\n\n\
**stderr:**\n`{err or 'no error'}`\n\n**stdout:**\n``{out or 'no output'}`` "
    await message.edit_or_send_as_file(text=output,
                                       parse_mode='md',
                                       filename="exec.txt",
                                       caption=cmd)


_KEY = '_OLD'
_EVAL_TASKS: Dict[asyncio.Future, str] = {}


@userge.on_cmd("eval", about={
    'header': "run python code line | lines",
    'flags': {
        '-s': "silent mode (hide STDIN)",
        '-p': "run in a private session",
        '-n': "spawn new main session and run",
        '-l': "list all running eval tasks",
        '-c': "cancel specific running eval task",
        '-ca': "cancel all running eval tasks"
    },
    'usage': "{tr}eval [flag] [code lines]",
    'examples': [
        "{tr}eval print('Userge')", "{tr}eval -s print('Userge')",
        "{tr}eval 5 + 6", "{tr}eval -s 5 + 6",
        "{tr}eval -p x = 'private_value'", "{tr}eval -n y = 'new_value'",
        "{tr}eval -c2", "{tr}eval -ca", "{tr}eval -l"]}, allow_channels=False)
async def eval_(message: Message):
    """ run python code """
    for t in tuple(_EVAL_TASKS):
        if t.done():
            del _EVAL_TASKS[t]

    flags = message.flags
    size = len(_EVAL_TASKS)
    if '-l' in flags:
        if _EVAL_TASKS:
            out = "**Eval Tasks**\n\n"
            i = 0
            for c in _EVAL_TASKS.values():
                out += f"**{i}** - `{c}`\n"
                i += 1
            out += f"\nuse `{Config.CMD_TRIGGER}eval -c[id]` to Cancel"
            await message.edit(out)
        else:
            await message.edit("No running eval tasks !", del_in=5)
        return
    if ('-c' in flags or '-ca' in flags) and size == 0:
        await message.edit("No running eval tasks !", del_in=5)
        return
    if '-ca' in flags:
        for t in _EVAL_TASKS:
            t.cancel()
        await message.edit(f"Canceled all running eval tasks [{size}] !", del_in=5)
        return
    if '-c' in flags:
        t_id = int(flags.get('-c', -1))
        if t_id < 0 or t_id >= size:
            await message.edit(f"Invalid eval task id [{t_id}] !", del_in=5)
            return
        list(_EVAL_TASKS)[t_id].cancel()
        await message.edit(f"Canceled eval task [{t_id}] !", del_in=5)
        return

    cmd = await init_func(message)
    if cmd is None:
        return

    _flags = []
    for _ in range(3):
        _found = False
        for f in ('-s', '-p', '-n'):
            if cmd.startswith(f):
                _found = True
                _flags.append(f)
                cmd = cmd[len(f):].strip()
                if not cmd:
                    break
        if not _found or not cmd:
            break

    if not cmd:
        await message.err("Unable to Parse Input!")
        return

    silent_mode = '-s' in _flags
    if '-n' in _flags:
        context_type = _ContextType.NEW
    elif '-p' in _flags:
        context_type = _ContextType.PRIVATE
    else:
        context_type = _ContextType.GLOBAL

    async def _callback(output: Optional[str], errored: bool):
        final = ""
        if not silent_mode:
            final += f"**>** ```{cmd}```\n\n"
        if isinstance(output, str):
            output = output.strip()
            if output == '':
                output = None
        if output is not None:
            final += f"**>>** ```{output}```"
        if errored and message.chat.type in ("group", "supergroup", "channel"):
            msg_id = await CHANNEL.log(final)
            await msg.edit(f"**Logs**: {CHANNEL.get_link(msg_id)}")
        elif final:
            await msg.edit_or_send_as_file(text=final,
                                           parse_mode='md',
                                           filename="eval.txt",
                                           caption=cmd)
        else:
            await msg.delete()

    msg = message
    replied = message.reply_to_message
    if (replied and replied.from_user
            and replied.from_user.is_self and isinstance(replied.text, Str)
            and str(replied.text.html).startswith("<b>></b> <pre>")):
        msg = replied

    await msg.edit("`Executing eval ...`", parse_mode='md')

    _g, _l = _context(
        context_type, userge=userge, message=message, replied=message.reply_to_message)
    l_d = {}
    try:
        exec(_wrap_code(cmd, _l.keys()), _g, l_d)  # nosec pylint: disable=W0122
    except Exception:  # pylint: disable=broad-except
        _g[_KEY] = _l
        await _callback(traceback.format_exc(), True)
        return
    future = asyncio.get_event_loop().create_future()
    pool.submit_thread(_run_coro, future, l_d['__aexec'](*_l.values()), _callback)
    hint = cmd.split('\n')[0]
    _EVAL_TASKS[future] = hint[:25] + "..." if len(hint) > 25 else hint

    with msg.cancel_callback(future.cancel):
        try:
            await future
        except asyncio.CancelledError:
            await asyncio.gather(msg.canceled(),
                                 CHANNEL.log(f"**EVAL Process Canceled!**\n\n```{cmd}```"))
        finally:
            _EVAL_TASKS.pop(future, None)


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
        parsed_cmd = parse_py_template(cmd, message)
    except Exception as e:  # pylint: disable=broad-except
        await message.err(str(e))
        await CHANNEL.log(f"**Exception**: {type(e).__name__}\n**Message**: " + str(e))
        return
    try:
        t_obj = await Term.execute(parsed_cmd)  # type: Term
    except Exception as t_e:  # pylint: disable=broad-except
        await message.err(str(t_e))
        return

    cur_user = getuser()
    try:
        uid = geteuid()
    except ImportError:
        uid = 1
    prefix = f"<b>{cur_user}:~#</b>" if uid == 0 else f"<b>{cur_user}:~$</b>"
    output = f"{prefix} <pre>{cmd}</pre>\n"

    async def _worker():
        await t_obj.wait()
        while not t_obj.finished:
            await message.edit(f"{output}<pre>{await t_obj.read_line()}</pre>", parse_mode='html')
            try:
                await asyncio.wait_for(t_obj.finish_listener, Config.EDIT_SLEEP_TIMEOUT)
            except asyncio.TimeoutError:
                pass

    def _on_cancel():
        t_obj.cancel()
        task.cancel()

    task = asyncio.create_task(_worker())
    with message.cancel_callback(_on_cancel):
        try:
            await task
        except asyncio.CancelledError:
            await message.canceled(reply=True)
            return

    out_data = f"{output}<pre>{await t_obj.get_output()}</pre>\n{prefix}"
    await message.edit_or_send_as_file(
        out_data, parse_mode='html', filename="term.txt", caption=cmd)


async def init_func(message: Message):
    cmd = message.input_str
    if not cmd:
        await message.err("No Command Found!")
        return None
    if "config.env" in cmd:
        await message.edit("`That's a dangerous operation! Not Permitted!`")
        return None
    return cmd


def parse_py_template(cmd: str, msg: Message):
    glo, loc = _context(_ContextType.PRIVATE, message=msg, replied=msg.reply_to_message)

    def replacer(mobj):
        return shlex.quote(str(eval(mobj.expand(r"\1"), glo, loc)))  # nosec pylint: disable=W0123
    return re.sub(r"{{(.+?)}}", replacer, cmd)


class _ContextType(Enum):
    GLOBAL = 0
    PRIVATE = 1
    NEW = 2


def _context(context_type: _ContextType, **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if context_type == _ContextType.NEW:
        try:
            del globals()[_KEY]
        except KeyError:
            pass
    if _KEY not in globals():
        globals()[_KEY] = globals().copy()
    _g = globals()[_KEY]
    if context_type == _ContextType.PRIVATE:
        _g = _g.copy()
    _l = _g.pop(_KEY, {})
    _l.update(kwargs)
    return _g, _l


def _wrap_code(code: str, args: Iterable[str]) -> str:
    head = "async def __aexec(" + ', '.join(args) + "):\n try:\n  "
    tail = "\n finally: globals()['" + _KEY + "'] = locals()"
    if '\n' in code:
        code = code.replace('\n', '\n  ')
    elif (any(True for k_ in keyword.kwlist if k_ not in (
            'True', 'False', 'None', 'lambda', 'await') and code.startswith(f"{k_} "))
          or ('=' in code and '==' not in code)):
        code = f"\n  {code}"
    else:
        code = f"\n  return {code}"
    return head + code + tail


def _run_coro(future: asyncio.Future, coro: Awaitable[Any],
              callback: Callable[[str, bool], Awaitable[Any]]) -> None:
    loop = asyncio.new_event_loop()
    task = loop.create_task(coro)
    userge.loop.call_soon_threadsafe(future.add_done_callback,
                                     lambda _: (loop.is_running() and future.cancelled()
                                                and loop.call_soon_threadsafe(task.cancel)))
    try:
        ret, exc = None, None
        with redirect() as out:
            try:
                ret = loop.run_until_complete(task)
            except asyncio.CancelledError:
                return
            except Exception:  # pylint: disable=broad-except
                exc = traceback.format_exc().strip()
            output = exc or out.getvalue()
            if ret is not None:
                output += str(ret)
        loop.run_until_complete(callback(output, exc is not None))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        userge.loop.call_soon_threadsafe(lambda: future.done() or future.set_result(None))


_PROXIES = {}


class _Wrapper:
    def __init__(self, original):
        self._original = original

    def __getattr__(self, name: str):
        return getattr(_PROXIES.get(threading.currentThread().ident, self._original), name)


sys.stdout = _Wrapper(sys.stdout)
sys.__stdout__ = _Wrapper(sys.__stdout__)
sys.stderr = _Wrapper(sys.stderr)
sys.__stderr__ = _Wrapper(sys.__stderr__)


@contextmanager
def redirect() -> io.StringIO:
    ident = threading.currentThread().ident
    source = io.StringIO()
    _PROXIES[ident] = source
    try:
        yield source
    finally:
        del _PROXIES[ident]
        source.close()


class Term:
    """ live update term class """

    def __init__(self, process: asyncio.subprocess.Process) -> None:
        self._process = process
        self._output = b''
        self._output_line = b''
        self._lock = asyncio.Lock()
        self._event = asyncio.Event()
        self._loop = asyncio.get_event_loop()
        self._flag = False
        self._finished = False
        self._finish_listener = self._loop.create_future()

    def _finish(self) -> None:
        self._finished = True
        if not self._finish_listener.done():
            self._finish_listener.set_result(None)

    def cancel(self) -> None:
        self._process.kill()
        self._event.set()
        self._finish()

    @property
    def finished(self) -> bool:
        return self._finished

    @property
    def finish_listener(self) -> asyncio.Future:
        if self._finish_listener.done():
            self._finish_listener = self._loop.create_future()
        return self._finish_listener

    async def wait(self) -> None:
        await self._event.wait()

    async def read_line(self) -> str:
        async with self._lock:
            return self._output_line.decode('utf-8', 'replace').strip()

    async def get_output(self) -> str:
        async with self._lock:
            return self._output.decode('utf-8', 'replace').strip()

    async def _append(self, line: bytes) -> None:
        async with self._lock:
            self._output_line = line
            self._output += line
        if not self._flag:
            self._loop.call_later(1, self._event.set)
            self._flag = True

    async def _read_stdout(self) -> None:
        while True:
            line = await self._process.stdout.readline()
            if not line:
                break
            await self._append(line)

    async def _read_stderr(self) -> None:
        while True:
            line = await self._process.stderr.readline()
            if not line:
                break
            await self._append(line)

    async def worker(self) -> None:
        await asyncio.wait([self._read_stdout(), self._read_stderr()])
        await self._process.wait()
        self._event.set()
        self._finish()

    @classmethod
    async def execute(cls, cmd: str) -> 'Term':
        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        t_obj = cls(process)
        asyncio.get_event_loop().create_task(t_obj.worker())
        return t_obj
