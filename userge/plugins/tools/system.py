""" system commands """
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import time
import asyncio
import shutil

from pyrogram.types import User

from userge.core.ext import RawClient
from userge import userge, Message, Config, get_collection
from userge.utils import terminate

SAVED_SETTINGS = get_collection("CONFIGS")
MAX_IDLE_TIME = 300
LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)


async def _init() -> None:
    global MAX_IDLE_TIME  # pylint: disable=global-statement
    d_s = await SAVED_SETTINGS.find_one({'_id': 'DYNO_SAVER'})
    if d_s:
        Config.RUN_DYNO_SAVER = bool(d_s['on'])
        MAX_IDLE_TIME = int(d_s['timeout'])


@userge.on_cmd('restart', about={
    'header': "Restarts the bot and reload all plugins",
    'flags': {
        '-h': "restart heroku dyno",
        '-t': "clean temp loaded plugins",
        '-d': "clean working folder"},
    'usage': "{tr}restart [flag | flags]",
    'examples': "{tr}restart -t -d"}, del_pre=True, allow_channels=False)
async def restart_(message: Message):
    """ restart userge """
    await message.edit("Restarting Userge Services", log=__name__)
    LOG.info("USERGE Services - Restart initiated")
    if 't' in message.flags:
        shutil.rmtree(Config.TMP_PATH, ignore_errors=True)
    if 'd' in message.flags:
        shutil.rmtree(Config.DOWN_PATH, ignore_errors=True)
    if Config.HEROKU_APP and 'h' in message.flags:
        await message.edit(
            '`Heroku app found, trying to restart dyno...\nthis will take upto 30 sec`', del_in=3)
        Config.HEROKU_APP.restart()
        time.sleep(30)
    else:
        await message.edit("finalizing...", del_in=1)
        asyncio.get_event_loop().create_task(userge.restart())


@userge.on_cmd("shutdown", about={'header': "shutdown userge :)"}, allow_channels=False)
async def shutdown_(message: Message) -> None:
    """ shutdown userge """
    await message.edit("`shutting down ...`")
    if Config.HEROKU_APP:
        try:
            Config.HEROKU_APP.process_formation()['worker'].scale(0)
        except Exception as h_e:  # pylint: disable=broad-except
            await message.edit(f"**heroku error** : `{h_e}`")
            await asyncio.sleep(3)
    else:
        await asyncio.sleep(1)
    await message.delete()
    terminate()


@userge.on_cmd("die", about={
    'header': "set auto heroku dyno off timeout",
    'flags': {'-t': "input offline timeout in min : default to 5min"},
    'usage': "{tr}die [flags]",
    'examples': ["{tr}die", "{tr}die -t5"]}, allow_channels=False)
async def die_(message: Message) -> None:
    """ set offline timeout to die userge """
    global MAX_IDLE_TIME  # pylint: disable=global-statement
    if not Config.HEROKU_APP:
        await message.err("`heroku app not detected !`")
        return
    await message.edit('`processing ...`')
    if Config.RUN_DYNO_SAVER:
        if isinstance(Config.RUN_DYNO_SAVER, asyncio.Task):
            Config.RUN_DYNO_SAVER.cancel()
        Config.RUN_DYNO_SAVER = False
        SAVED_SETTINGS.update_one({'_id': 'DYNO_SAVER'},
                                  {"$set": {'on': False}}, upsert=True)
        await message.edit('auto heroku dyno off worker has been **stopped**',
                           del_in=5, log=__name__)
        return
    time_in_min = int(message.flags.get('-t', 5))
    if time_in_min < 5:
        await message.err(f"`please set higher value [{time_in_min}] !`")
        return
    MAX_IDLE_TIME = time_in_min * 60
    SAVED_SETTINGS.update_one({'_id': 'DYNO_SAVER'},
                              {"$set": {'on': True, 'timeout': MAX_IDLE_TIME}}, upsert=True)
    await message.edit('auto heroku dyno off worker has been **started** '
                       f'[`{time_in_min}`min]', del_in=3, log=__name__)
    Config.RUN_DYNO_SAVER = asyncio.get_event_loop().create_task(_dyno_saver_worker())


@userge.on_cmd("setvar", about={
    'header': "set var in heroku",
    'usage': "{tr}setvar [var_name] [var_data]",
    'examples': "{tr}setvar WORKERS 4"})
async def setvar_(message: Message) -> None:
    """ set var (heroku) """
    if not Config.HEROKU_APP:
        await message.err("`heroku app not detected !`")
        return
    if not message.input_str:
        await message.err("`input needed !`")
        return
    var_name, var_data = message.input_str.split(maxsplit=1)
    if not var_data:
        await message.err("`var data needed !`")
        return
    var_name = var_name.strip()
    var_data = var_data.strip()
    heroku_vars = Config.HEROKU_APP.config()
    if var_name in heroku_vars:
        await CHANNEL.log(
            f"#HEROKU_VAR #SET #UPDATED\n\n`{var_name}` = `{var_data}`")
        await message.edit(f"`var {var_name} updated and forwarded to log channel !`", del_in=3)
    else:
        await CHANNEL.log(
            f"#HEROKU_VAR #SET #ADDED\n\n`{var_name}` = `{var_data}`")
        await message.edit(f"`var {var_name} added and forwarded to log channel !`", del_in=3)
    heroku_vars[var_name] = var_data


@userge.on_cmd("delvar", about={
    'header': "del var in heroku",
    'usage': "{tr}delvar [var_name]",
    'examples': "{tr}delvar WORKERS"})
async def delvar_(message: Message) -> None:
    """ del var (heroku) """
    if not Config.HEROKU_APP:
        await message.err("`heroku app not detected !`")
        return
    if not message.input_str:
        await message.err("`var name needed !`")
        return
    var_name = message.input_str.strip()
    heroku_vars = Config.HEROKU_APP.config()
    if var_name not in heroku_vars:
        await message.err(f"`var {var_name} not found !`")
        return
    await CHANNEL.log(f"#HEROKU_VAR #DEL\n\n`{var_name}` = `{heroku_vars[var_name]}`")
    await message.edit(f"`var {var_name} deleted and forwarded to log channel !`", del_in=3)
    del heroku_vars[var_name]


@userge.on_cmd("getvar", about={
    'header': "get var in heroku",
    'usage': "{tr}getvar [var_name]",
    'examples': "{tr}getvar WORKERS 4"})
async def getvar_(message: Message) -> None:
    """ get var (heroku) """
    if not Config.HEROKU_APP:
        await message.err("`heroku app not detected !`")
        return
    if not message.input_str:
        await message.err("`var name needed !`")
        return
    var_name = message.input_str.strip()
    heroku_vars = Config.HEROKU_APP.config()
    if var_name not in heroku_vars:
        await message.err(f"`var {var_name} not found !`")
        return
    await CHANNEL.log(f"#HEROKU_VAR #GET\n\n`{var_name}` = `{heroku_vars[var_name]}`")
    await message.edit(f"`var {var_name} forwarded to log channel !`", del_in=3)


@userge.on_cmd("sleep (\\d+)", about={
    'header': "sleep userge :P",
    'usage': "{tr}sleep [timeout in seconds]"}, allow_channels=False)
async def sleep_(message: Message) -> None:
    """ sleep userge """
    seconds = int(message.matches[0].group(1))
    await message.edit(f"`sleeping {seconds} seconds...`")
    asyncio.get_event_loop().create_task(_slp_wrkr(seconds))


async def _slp_wrkr(seconds: int) -> None:
    await userge.stop()
    await asyncio.sleep(seconds)
    await userge.reload_plugins()
    await userge.start()


@userge.on_user_status()
async def _user_status(_, user: User) -> None:
    Config.STATUS = user.status


@userge.add_task
async def _dyno_saver_worker() -> None:
    count = 0
    check_delay = 5
    offline_start_time = time.time()
    while Config.RUN_DYNO_SAVER:
        if not count % check_delay and (
            Config.STATUS is None or Config.STATUS != "online"
        ):
            if Config.STATUS is None:
                LOG.info("< bot client found ! >")
            else:
                LOG.info("< state changed to offline ! >")
                offline_start_time = time.time()
            warned = False
            while Config.RUN_DYNO_SAVER and (
                    Config.STATUS is None or Config.STATUS != "online"):
                if not count % check_delay:
                    if Config.STATUS is None:
                        offline_start_time = RawClient.LAST_OUTGOING_TIME
                    current_idle_time = int((time.time() - offline_start_time))
                    if current_idle_time < 5:
                        warned = False
                    if current_idle_time >= MAX_IDLE_TIME:
                        try:
                            Config.HEROKU_APP.process_formation()['worker'].scale(0)
                        except Exception as h_e:  # pylint: disable=broad-except
                            LOG.error(f"heroku app error : {h_e}")
                            offline_start_time += 20
                            await asyncio.sleep(10)
                            continue
                        LOG.info("< successfully killed heroku dyno ! >")
                        await CHANNEL.log("heroku dyno killed !")
                        terminate()
                        return
                    prog = round(current_idle_time * 100 / MAX_IDLE_TIME, 2)
                    mins = int(MAX_IDLE_TIME / 60)
                    if prog >= 75 and not warned:
                        rem = int((100 - prog) * MAX_IDLE_TIME / 100)
                        await CHANNEL.log(
                            f"#WARNING\n\ndyno kill worker `{prog}%` completed !"
                            f"\n`{rem}`s remaining !")
                        warned = True
                    LOG.info(f"< dyno kill worker ... ({prog}%)({mins}) >")
                await asyncio.sleep(1)
                count += 1
            LOG.info("< state changed to online ! >")
        await asyncio.sleep(1)
        count += 1
    if count:
        LOG.info("< auto heroku dyno off worker has been stopped! >")
