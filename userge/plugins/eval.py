import io
import os
import sys
import traceback
from userge import userge, Config

log = userge.getLogger(__name__)


@userge.on_cmd("eval", about="run eval")
async def eval_(_, message: userge.MSG):
    await message.edit("Processing ...")
    cmd = message.text.split(" ", maxsplit=1)[1]
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