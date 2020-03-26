import io
import sys
import traceback
from getpass import getuser
from os import geteuid
from userge import userge, Config, Message
from userge.utils import runcmd


@userge.on_cmd("eval", about="""\
__run python code line | lines__

**Usage:**

    `.eval [code lines]
    
**Example:**

    `.eval print('Userge')`""")
async def eval_(message: Message):
    cmd = await init_func(message)

    if cmd is None:
        return

    old_stderr = sys.stderr
    old_stdout = sys.stdout

    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()

    stdout, stderr, exc = None, None, None

    async def aexec(code, userge, message):
        exec("async def __aexec(userge, message):\n " + \
                '\n '.join(line for line in code.split('\n')))

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

    output = "**EVAL**:\n```{}```\n\n\
**OUTPUT**:\n```{}```".format(cmd, evaluation.strip())

    if len(output) > Config.MAX_MESSAGE_LENGTH:
        await message.send_as_file(text=output,
                                   filename="eval.txt",
                                   caption=cmd)

    else:
        await message.edit(output)


@userge.on_cmd("exec", about="""\
__run shell commands__

**Usage:**

    `.exec [commands]
    
**Example:**

    `.exec echo "Userge"`""")
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

    if len(output) > Config.MAX_MESSAGE_LENGTH:
        await message.send_as_file(text=output,
                                   filename="exec.txt",
                                   caption=cmd)

    else:
        await message.edit(output)


@userge.on_cmd("term", about="""\
__run terminal commands__

**Usage:**

    `.term [commands]
    
**Example:**

    `.term echo "Userge"`""")
async def term_(message: Message):
    cmd = await init_func(message)

    if cmd is None:
        return

    out, err, _, _ = await runcmd(cmd)

    output = str(out) + str(err)

    if len(output) > Config.MAX_MESSAGE_LENGTH:
        await message.send_as_file(text=output,
                                   filename="term.txt",
                                   caption=cmd)

    else:
        try:
            uid = geteuid()

        except ImportError:
            uid = 1

        curruser = getuser()

        if uid == 0:
            await message.edit(f"`{curruser}:~# {cmd}\n{output}`")

        else:
            await message.edit(f"`{curruser}:~$ {cmd}\n{output}`")


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
