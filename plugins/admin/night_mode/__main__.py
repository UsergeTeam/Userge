from datetime import datetime, timedelta

import pytz
from apscheduler.jobstores.base import ConflictingIdError
from pyrogram.errors import ChatAdminRequired, ChannelInvalid, ChannelPrivate, ChatNotModified
from pyrogram.types import ChatPermissions

from userge import userge, Message
from ..night_mode import scheduler, TZ

CHANNEL = userge.getCLogger(__name__)
LOGGER = userge.getLogger(__name__)

TIME_ZONE = pytz.timezone(TZ)


@userge.on_start
async def _init():
    if bool(scheduler.get_jobs()):
        scheduler.start()


@userge.on_cmd("nightmode", about={
    'header': "Enable or disable nightmode (locks the chat at specified intervals everyday)",
    'flags': {
        '-s': "Specify starting time in 24hr format.",
        '-e': "Specify duration in hrs / minute",
        '-d': "Disable nightmode for chat."},
    'examples': [
        "{tr}nightmode -s=23:53 -e=6h",
        "{tr}nightmode -s=23:50 -e=120m"]},
    allow_bots=False, allow_channels=False)
async def nightmode_handler(msg: Message):
    """ Activate NightMode in your group"""
    flags = msg.flags

    chat_id = msg.chat.id

    if "-d" in flags:
        job = scheduler.get_job(job_id=f"enable_nightmode_{chat_id}")
        if job:
            scheduler.remove_job(job_id=f"enable_nightmode_{chat_id}")
            scheduler.remove_job(job_id=f"disable_nightmode_{chat_id}")
            if not bool(scheduler.get_jobs()) and bool(scheduler.state):
                scheduler.shutdown()
            return await msg.edit('nightmode disabled.')
        return await msg.err("nightmode isn't enabled in this chat.")

    start = flags.get('-s', '00:00')
    now = datetime.now(TIME_ZONE)

    try:
        start_timestamp = TIME_ZONE.localize(
            datetime.strptime(
                (now.strftime('%m:%d:%Y - ') + start),
                '%m:%d:%Y - %H:%M'))
    except ValueError:
        return await msg.err("Invalid time format. Use HH:MM format.")
    lock_dur = extract_time((flags.get('-e', '6h')).lower())

    if not lock_dur:
        return await msg.err(
            'Invalid time duration. Use proper format.'
            '\nExample: 6h (for 6 hours), 10m for 10 minutes.')

    if start_timestamp < now:
        start_timestamp = start_timestamp + timedelta(days=1)
    end_time_stamp = start_timestamp + timedelta(seconds=int(lock_dur))
    try:
        # schedule to enable nightmode
        scheduler.add_job(
            mute_chat,
            'interval',
            [chat_id],
            id=f"enable_nightmode_{chat_id}",
            days=1,
            next_run_time=start_timestamp,
            max_instances=50,
            misfire_grace_time=None)

        # schedule to disable nightmode
        scheduler.add_job(
            un_mute_chat,
            'interval',
            [chat_id,
             msg.chat.permissions],
            id=f"disable_nightmode_{chat_id}",
            days=1,
            next_run_time=end_time_stamp,
            max_instances=50,
            misfire_grace_time=None)
    except ConflictingIdError:
        return await msg.edit(
            'already a schedule is running in this chat. Disable it using `-d` flag.')
    await msg.edit(
        'Successfully enabled nightmode in this chat.\n'
        f'Group will be locked at {start_timestamp.strftime("%H:%M:%S")}'
        f' and will be opened after {flags.get("-e", "6h")} everyday.')
    if not bool(scheduler.state):
        scheduler.start()


async def un_mute_chat(chat_id: int, perm: ChatPermissions):
    try:
        await userge.set_chat_permissions(chat_id, perm)
    except ChatAdminRequired:
        await CHANNEL.log(
            f"#NIGHT_MODE_FAIL\nFailed to turn off nightmode at `{chat_id}`,"
            f"since userge is not an admin in chat `{chat_id}`")
    except (ChannelInvalid, ChannelPrivate):
        scheduler.remove_job(f"enable_nightmode_{chat_id}")
        scheduler.remove_job(f"disable_nightmode_{chat_id}")
        await CHANNEL.log(
            f"#NIGHT_MODE_FAIL\nFailed to turn off nightmode at `{chat_id}`,"
            f"since userge is not present in chat `{chat_id}`"
            " Removed group from list.")
    except ChatNotModified:
        pass
    except Exception as e:
        await CHANNEL.log(
            f"#NIGHT_MODE_FAIL\nFailed to turn off nightmode at `{chat_id}`\n"
            f"ERROR: `{e}`")
        await LOGGER.exception(e)
    else:
        job = scheduler.get_job(f"enable_nightmode_{chat_id}")
        close_at = job.next_run_time
        await userge.send_message(
            chat_id,
            f"#AUTOMATED_HANDLER\nGroup is Opening.\nWill be closed at {close_at}")
        await CHANNEL.log(
            f"#NIGHT_MODE_SUCCESS\nSuccessfully turned off nightmode at `{chat_id}`,")


async def mute_chat(chat_id: int):
    try:
        await userge.set_chat_permissions(chat_id, ChatPermissions())
    except ChatAdminRequired:
        await CHANNEL.log(
            f"#NIGHT_MODE_FAIL\nFailed to enable nightmode at `{chat_id}`,"
            f"since userge is not an admin in chat `{chat_id}`")
    except (ChannelInvalid, ChannelPrivate):
        scheduler.remove_job(f"enable_nightmode_{chat_id}")
        scheduler.remove_job(f"disable_nightmode_{chat_id}")
        await CHANNEL.log(
            f"#NIGHT_MODE_FAIL\nFailed to enable nightmode at `{chat_id}`,"
            f"since userge is not present in chat `{chat_id}`"
            " Removed group from list.")
    except ChatNotModified:
        pass
    except Exception as e:
        await CHANNEL.log(
            f"#NIGHT_MODE_FAIL\nFailed to enable nightmode at `{chat_id}`\n"
            f"ERROR: `{e}`")
        await LOGGER.exception(e)
    else:
        job = scheduler.get_job(f"disable_nightmode_{chat_id}")
        open_at = job.next_run_time
        await userge.send_message(
            chat_id,
            f"#AUTOMATED_HANDLER\nGroup is closing.\nWill be opened at {open_at}")
        await CHANNEL.log(
            f"#NIGHT_MODE_SUCCESS\nSuccessfully turned on nightmode at `{chat_id}`,")


def extract_time(time_val: str):
    if any(time_val.endswith(unit) for unit in ('m', 'h')):
        unit = time_val[-1]
        time_num = time_val[:-1]
        if not time_num.isdigit():
            return ""
        if unit == 'm':
            time = int(time_num) * 60
        elif unit == 'h':
            time = int(time_num) * 60 * 60
        else:
            return ""
        return time
    return ""
