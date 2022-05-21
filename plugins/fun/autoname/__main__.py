""" Auto Update Name """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

# By @Krishna_Singhal
# Base Plugin by @Phyco-Ninja

import asyncio
from collections import deque

from pyrogram.errors import FloodWait

from userge import userge, Message, get_collection

UPDATION = False
AUTONAME_TIMEOUT = 60
NAME = None

CHANNEL = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)

USER_DATA = get_collection("CONFIGS")

FONTS_ = [
    "abcdefghijklmnopqrstuvwxyz",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ",
    "₳฿₵ĐɆ₣₲ⱧłJ₭Ⱡ₥₦Ø₱QⱤ₴₮ɄV₩ӾɎⱫ",
    "αв¢∂єfgнιנкℓмиσρqяѕтυνωχуz",
    "ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ",
    "🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩",
    "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉",
    "🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ",
    "αвc∂εғgнιנкℓмησρqяsтυvωxүz",
    "卂乃匚ᗪ乇千Ꮆ卄丨ﾌҜㄥ爪几ㄖ卩Ɋ尺丂ㄒㄩᐯ山乂ㄚ乙",
    "ᎪbᏟᎠᎬfᎶhᎥjᏦᏞmᏁᎾᏢqᏒsᏆuᏉᎳxᎽᏃ",
    "αɓ૮∂εƒɠɦเʝҡℓɱɳσρφ૨รƭµѵωאყƶ",
    "aвcdeғgнιjĸlмnopqrѕтυvwхyz",
    "ДБCDΞFGHIJҜLMИФPǪЯSΓЦVЩЖУZ",
    "ꋬꃳꉔ꒯ꏂꊰꍌꁝ꒐꒻ꀘ꒒ꂵꋊꄲꉣꆰꋪꇙ꓄꒤꒦ꅐꉧꌦꁴ",
    "คც८ძ૯Բ૭ҺɿʆқՆɱՈ૦ƿҩՐς੮υ౮ω૪עઽ",
    "ᗩᗷᑕᗪEᖴGᕼIᒍKᒪᗰᑎOᑭᑫᖇᔕTᑌᐯᗯ᙭Yᘔ",
    "ᏗᏰፈᎴᏋᎦᎶᏂᎥᏠᏦᏝᎷᏁᎧᎮᎤᏒᏕᏖᏬᏉᏇጀᎩፚ"
]


@userge.on_start
async def _init() -> None:
    global UPDATION, AUTONAME_TIMEOUT, NAME  # pylint: disable=global-statement
    data = await USER_DATA.find_one({'_id': 'UPDATION'})
    if data:
        UPDATION = data['on']
    if UPDATION:
        NAME = data['NametoUpdate']
    a_t = await USER_DATA.find_one({'_id': 'AUTONAME_TIMEOUT'})
    if a_t:
        AUTONAME_TIMEOUT = a_t['data']


@userge.on_cmd("autoname", about={
    'header': "Auto Updates your Profile name with Diffrent Fonts",
    'usage': "{tr}autoname\n{tr}autoname [new name]"}, allow_via_bot=False)
async def auto_name(msg: Message):
    global UPDATION, NAME  # pylint: disable=global-statement
    if UPDATION:
        if isinstance(UPDATION, asyncio.Task):
            UPDATION.cancel()
        UPDATION = False

        await USER_DATA.update_one({'_id': 'UPDATION'},
                                   {"$set": {'on': False}},
                                   upsert=True)
        await asyncio.sleep(1)

        # Reverting Old Name
        data = await USER_DATA.find_one({'_id': 'UPDATION'})
        fname = data['fname']
        await msg.edit("`Setting up Original Name...`")
        await userge.update_profile(first_name=fname)
        await USER_DATA.delete_one({'_id': 'UPDATION', 'fname': fname})
        await msg.edit(
            "Auto Name Updation is **Stopped** Successfully...", log=__name__, del_in=5)
        return
    NAME = msg.input_str
    if not NAME:
        NAME = msg.from_user.first_name
    # Store current name to revert
    first_name = (await userge.get_me()).first_name
    await USER_DATA.update_one(
        {'_id': 'UPDATION'},
        {"$set": {'on': True, 'fname': first_name, 'NametoUpdate': NAME}},
        upsert=True
    )
    await msg.edit(
        "Auto Name Updation is **Started** Successfully...",
        log=__name__, del_in=3
    )
    loop = asyncio.get_event_loop()
    UPDATION = loop.create_task(_autoname_worker())


@userge.on_cmd("santo", about={
    'header': "Set Auto Name timeout",
    'usage': "{tr}santo [timeout in seconds]",
    'examples': "{tr}santo 30"})
async def set_name_timeout(message: Message):
    """ set Auto Name timeout """
    global AUTONAME_TIMEOUT  # pylint: disable=global-statement
    t_o = int(message.input_str)
    if t_o < 30:
        await message.err("too short! (minimum 30 sec)")
        return
    await message.edit("`Setting Auto Name timeout...`")
    AUTONAME_TIMEOUT = t_o
    await USER_DATA.update_one(
        {'_id': 'AUTONAME_TIMEOUT'}, {"$set": {'data': t_o}}, upsert=True)
    await message.edit(
        f"`Set Auto Name timeout as {t_o} seconds!`", del_in=5)


@userge.on_cmd("vanto", about={'header': "View Auto Name timeout"})
async def view_name_timeout(message: Message):
    """ view Auto Name timeout """
    await message.edit(
        f"`Name will be updated after {AUTONAME_TIMEOUT} seconds!`",
        del_in=5)


@userge.add_task
async def _autoname_worker():
    global NAME, FONTS_  # pylint: disable=global-statement
    animation = "|/-\\"
    anicount = 0
    FONTS_ = deque(FONTS_)
    while UPDATION and NAME:
        if not UPDATION:
            break
        F = list(FONTS_)
        cur_list = list(F[0])
        to_rep_list = list(F[1])
        for ch in NAME:
            if not UPDATION:
                break
            if ch in cur_list:
                rep_ch = to_rep_list[cur_list.index(ch)]
                NAME = NAME.replace(ch, rep_ch, 1)
                fname = animation[anicount] + ' $ ' + NAME + ' $ ' + animation[anicount]
                try:
                    await userge.update_profile(first_name=fname)
                except FloodWait as s_c:
                    await CHANNEL.log(f"Sleeping for {s_c} seconds because of Autoname.")
                    await asyncio.sleep(s_c.x)
                except Exception as e:
                    LOG.error(e)
                    await CHANNEL.log(f"**ERROR:** `{str(e)}")
                await asyncio.sleep(AUTONAME_TIMEOUT)
                anicount = (anicount + 1) % 4
        FONTS_.rotate(-1)
