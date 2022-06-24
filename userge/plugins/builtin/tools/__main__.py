""" set or view your timeouts """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

from datetime import datetime

from pyrogram.raw.functions import Ping

from userge import userge, Message, logging, config, pool, get_collection

SAVED_SETTINGS = get_collection("CONFIGS")


@userge.on_start
async def _init() -> None:
    msg_t = await SAVED_SETTINGS.find_one({'_id': 'MSG_DELETE_TIMEOUT'})
    if msg_t:
        config.Dynamic.MSG_DELETE_TIMEOUT = msg_t['data']
    es_t = await SAVED_SETTINGS.find_one({'_id': 'EDIT_SLEEP_TIMEOUT'})
    if es_t:
        config.Dynamic.EDIT_SLEEP_TIMEOUT = es_t['data']


@userge.on_cmd("sdelto (\\d+)", about={
    'header': "Set auto message delete timeout",
    'usage': "{tr}sdelto [timeout in seconds]",
    'examples': "{tr}sdelto 15\n{tr}sdelto 0 : for disable deletion"})
async def set_delete_timeout(message: Message):
    """ set delete timeout """
    await message.edit("`Setting auto message delete timeout...`")

    t_o = int(message.matches[0].group(1))
    config.Dynamic.MSG_DELETE_TIMEOUT = t_o

    await SAVED_SETTINGS.update_one(
        {'_id': 'MSG_DELETE_TIMEOUT'}, {"$set": {'data': t_o}}, upsert=True)

    if t_o:
        await message.edit(
            f"`Set auto message delete timeout as {t_o} seconds!`", del_in=3)
    else:
        await message.edit("`Auto message deletion disabled!`", del_in=3)


@userge.on_cmd("vdelto", about={'header': "View auto message delete timeout"})
async def view_delete_timeout(message: Message):
    """ view delete timeout """
    if config.Dynamic.MSG_DELETE_TIMEOUT:
        await message.edit(
            f"`Messages will be deleted after {config.Dynamic.MSG_DELETE_TIMEOUT} seconds!`",
            del_in=5)
    else:
        await message.edit("`Auto message deletion disabled!`", del_in=3)


@userge.on_cmd("sesto (\\d+)", about={
    'header': "Set edit sleep timeout",
    'usage': "{tr}sesto [timeout in seconds]",
    'examples': "{tr}sesto 10"})
async def set_es_timeout(message: Message):
    """ set edit sleep timeout """
    t_o = int(message.matches[0].group(1))
    if t_o < 5:
        await message.err("too short! (min = 5sec)")
        return

    await message.edit("`Setting edit sleep timeout...`")
    config.Dynamic.EDIT_SLEEP_TIMEOUT = t_o

    await SAVED_SETTINGS.update_one(
        {'_id': 'EDIT_SLEEP_TIMEOUT'}, {"$set": {'data': t_o}}, upsert=True)

    await message.edit(
        f"`Set edit sleep timeout as {t_o} seconds!`", del_in=3)


@userge.on_cmd("vesto", about={'header': "View edit sleep timeout"})
async def view_es_timeout(message: Message):
    """ view edit sleep timeout """
    await message.edit(
        f"`Current edit sleep timeout = {config.Dynamic.EDIT_SLEEP_TIMEOUT} seconds!`",
        del_in=5)


@userge.on_cmd("cancel", about={
    'header': "Reply this to message you want to cancel",
    'flags': {'-a': "cancel all tasks"}})
async def cancel_(message: Message):
    """ cancel bg tasks """
    if '-a' in message.flags:
        ret = Message._call_all_cancel_callbacks()  # pylint: disable=protected-access
        if ret == 0:
            await message.err("nothing found to cancel", show_help=False)
        return

    replied = message.reply_to_message  # type: Message
    if replied:
        if not replied._call_cancel_callbacks():  # pylint: disable=protected-access
            await message.err("nothing found to cancel", show_help=False)
    else:
        await message.err("source not provided !", show_help=False)


@userge.on_cmd("json", about={
    'header': "message object to json",
    'usage': "reply {tr}json to any message"})
async def jsonify(message: Message):
    """ msg to json """
    msg = str(message.reply_to_message) if message.reply_to_message else str(message)
    await message.edit_or_send_as_file(text=msg, filename="json.txt", caption="Too Large")


@userge.on_cmd("ping", about={
    'header': "check how long it takes to ping your userbot"}, group=-1)
async def pingme(message: Message):
    """ ping tg servers """
    start = datetime.now()
    await message.client.invoke(Ping(ping_id=0))
    end = datetime.now()

    m_s = (end - start).microseconds / 1000
    await message.edit(f"**Pong!**\n`{m_s} ms`")


@userge.on_cmd("s", about={
    'header': "search commands or plugins",
    'flags': {'-p': "search plugin"},
    'examples': ["{tr}s wel", "{tr}s -p gdrive"]}, allow_channels=False)
async def search(message: Message):
    """ search commands """
    key = message.filtered_input_str
    if not key:
        await message.err("input not found")
        return

    plugins = '-p' in message.flags
    data = list(userge.manager.loaded_plugins if plugins else userge.manager.loaded_commands)

    found = [i for i in sorted(data) if key in i]
    out_str = '    '.join(found)

    if found:
        out = f"**--found {len(found)} {'plugin' if plugins else 'command'}(s) for-- : `{key}`**"
        out += f"\n\n`{out_str}`"
    else:
        out = f"__nothing found for__ : `{key}`"

    await message.edit(text=out, del_in=0)


@userge.on_cmd("logs", about={
    'header': "check userge logs",
    'flags': {
        '-h': "get heroku logs (default limit 100)",
        '-l': "get loader logs"},
    'examples': [
        "{tr}logs", "{tr}logs -h", "{tr}logs -h200", "{tr}logs -l"]
}, allow_channels=False)
async def check_logs(message: Message):
    """ check logs """
    await message.edit("`checking logs ...`")

    if '-h' in message.flags and config.HEROKU_APP:
        limit = int(message.flags.get('-h') or 100)
        logs = await pool.run_in_thread(config.HEROKU_APP.get_log)(lines=limit)

        await message.client.send_as_file(chat_id=message.chat.id,
                                          text=logs,
                                          filename='userge-heroku.log',
                                          caption=f'userge-heroku.log [ {limit} lines ]')
    else:
        filename = f"{'loader' if '-l' in message.flags else 'userge'}.log"
        await message.client.send_document(chat_id=message.chat.id,
                                           document=f"logs/{filename}",
                                           caption=filename)
    await message.delete()


_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


@userge.on_cmd("setlvl", about={
    'header': "set logger level, default to info",
    'types': ['debug', 'info', 'warning', 'error', 'critical'],
    'usage': "{tr}setlvl [level]",
    'examples': ["{tr}setlvl info", "{tr}setlvl debug"]})
async def set_level(message: Message):
    """ set logger level """
    await message.edit("`setting logger level ...`")
    level = message.input_str.lower()

    if level not in _LEVELS:
        await message.err("unknown level !")
        return

    for logger in (logging.getLogger(name) for name in logging.root.manager.loggerDict):
        logger.setLevel(_LEVELS[level])

    await message.edit(f"`successfully set logger level as` : **{level.upper()}**", del_in=3)
