# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['RawDecorator']

import os
import time
import asyncio
from traceback import format_exc
from functools import partial
from typing import List, Dict, Union, Any, Callable, Optional

from pyrogram import StopPropagation, ContinuePropagation
from pyrogram.filters import Filter as RawFilter
from pyrogram.types import Message as RawMessage, ChatMember
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired, PeerIdInvalid

from userge import logging, Config
from ...ext import RawClient
from ... import types, client as _client  # pylint: disable=unused-import

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  :::::  %s  :::::  !>>>"

_PYROFUNC = Callable[['types.bound.Message'], Any]
_TASK_1_START_TO = time.time()
_TASK_2_START_TO = time.time()

_B_ID = 0
_B_CMN_CHT: List[int] = []
_B_AD_CHT: Dict[int, ChatMember] = {}
_B_NM_CHT: Dict[int, ChatMember] = {}

_U_ID = 0
_U_AD_CHT: Dict[int, ChatMember] = {}
_U_NM_CHT: Dict[int, ChatMember] = {}

_CH_LKS: Dict[str, asyncio.Lock] = {}
_CH_LKS_LK = asyncio.Lock()
_INIT_LK = asyncio.Lock()


async def _update_u_cht(r_m: RawMessage) -> ChatMember:
    if r_m.chat.id not in {**_U_AD_CHT, **_U_NM_CHT}:
        user = await r_m.chat.get_member(_U_ID)
        user.can_all = None
        if user.status == "creator":
            user.can_all = True
        if user.status in ("creator", "administrator"):
            _U_AD_CHT[r_m.chat.id] = user
        else:
            _U_NM_CHT[r_m.chat.id] = user
    elif r_m.chat.id in _U_AD_CHT:
        user = _U_AD_CHT[r_m.chat.id]
    else:
        user = _U_NM_CHT[r_m.chat.id]
    return user


async def _update_b_cht(r_m: RawMessage) -> ChatMember:
    if r_m.chat.id not in {**_B_AD_CHT, **_B_NM_CHT}:
        bot = await r_m.chat.get_member(_B_ID)
        if bot.status == "administrator":
            _B_AD_CHT[r_m.chat.id] = bot
        else:
            _B_NM_CHT[r_m.chat.id] = bot
    elif r_m.chat.id in _B_AD_CHT:
        bot = _B_AD_CHT[r_m.chat.id]
    else:
        bot = _B_NM_CHT[r_m.chat.id]
    return bot


def _clear_cht() -> None:
    global _TASK_1_START_TO  # pylint: disable=global-statement
    _U_AD_CHT.clear()
    _U_NM_CHT.clear()
    _B_AD_CHT.clear()
    _B_NM_CHT.clear()
    _TASK_1_START_TO = time.time()


async def _init(r_c: Union['_client.Userge', '_client.UsergeBot'],
                r_m: RawMessage) -> None:
    global _U_ID, _B_ID  # pylint: disable=global-statement
    if r_m.from_user and (
        r_m.from_user.is_self or (
            r_m.from_user.id in Config.SUDO_USERS) or (
                r_m.from_user.id in Config.OWNER_ID)):
        RawClient.LAST_OUTGOING_TIME = time.time()
    async with _INIT_LK:
        if _U_ID and _B_ID:
            return
        if isinstance(r_c, _client.Userge):
            if not _U_ID:
                _U_ID = (await r_c.get_me()).id
            if RawClient.DUAL_MODE and not _B_ID:
                _B_ID = (await r_c.bot.get_me()).id
        else:
            if not _B_ID:
                _B_ID = (await r_c.get_me()).id
            if RawClient.DUAL_MODE and not _U_ID:
                _U_ID = (await r_c.ubot.get_me()).id


async def _raise_func(r_c: Union['_client.Userge', '_client.UsergeBot'],
                      chat_id: int, message_id: int, text: str) -> None:
    try:
        _sent = await r_c.send_message(
            chat_id=chat_id,
            text=f"< **ERROR** : {text} ! >",
            reply_to_message_id=message_id)
        await asyncio.sleep(5)
        await _sent.delete()
    except ChatAdminRequired:
        pass


async def _is_admin(r_c: Union['_client.Userge', '_client.UsergeBot'],
                    r_m: RawMessage) -> bool:
    if r_m.chat.type in ("private", "bot"):
        return False
    if round(time.time() - _TASK_1_START_TO) > 10:
        _clear_cht()
    if isinstance(r_c, _client.Userge):
        await _update_u_cht(r_m)
        return r_m.chat.id in _U_AD_CHT
    await _update_b_cht(r_m)
    return r_m.chat.id in _B_AD_CHT


def _get_chat_member(r_c: Union['_client.Userge', '_client.UsergeBot'],
                     r_m: RawMessage) -> Optional[ChatMember]:
    if r_m.chat.type in ("private", "bot"):
        return None
    if isinstance(r_c, _client.Userge):
        if r_m.chat.id in _U_AD_CHT:
            return _U_AD_CHT[r_m.chat.id]
        return _U_NM_CHT[r_m.chat.id]
    if r_m.chat.id in _B_AD_CHT:
        return _B_AD_CHT[r_m.chat.id]
    return _B_NM_CHT[r_m.chat.id]


async def _get_lock(key: str) -> asyncio.Lock:
    async with _CH_LKS_LK:
        if key not in _CH_LKS:
            _CH_LKS[key] = asyncio.Lock()
    return _CH_LKS[key]


async def _bot_is_present(r_c: Union['_client.Userge', '_client.UsergeBot'],
                          r_m: RawMessage) -> bool:
    global _TASK_2_START_TO  # pylint: disable=global-statement
    if isinstance(r_c, _client.Userge):
        if round(time.time() - _TASK_2_START_TO) > 10:
            try:
                chats = await r_c.get_common_chats(_B_ID)
                _B_CMN_CHT.clear()
                for chat in chats:
                    _B_CMN_CHT.append(chat.id)
            except PeerIdInvalid:
                pass
            _TASK_2_START_TO = time.time()
    else:
        if r_m.chat.id not in _B_CMN_CHT:
            _B_CMN_CHT.append(r_m.chat.id)
    return r_m.chat.id in _B_CMN_CHT


async def _both_are_admins(r_c: Union['_client.Userge', '_client.UsergeBot'],
                           r_m: RawMessage) -> bool:
    if not await _bot_is_present(r_c, r_m):
        return False
    return r_m.chat.id in _B_AD_CHT and r_m.chat.id in _U_AD_CHT


async def _both_have_perm(flt: Union['types.raw.Command', 'types.raw.Filter'],
                          r_c: Union['_client.Userge', '_client.UsergeBot'],
                          r_m: RawMessage) -> bool:
    if not await _bot_is_present(r_c, r_m):
        return False
    try:
        user = await _update_u_cht(r_m)
        bot = await _update_b_cht(r_m)
    except PeerIdInvalid:
        return False
    if flt.check_change_info_perm and not (
            (user.can_all or user.can_change_info) and bot.can_change_info):
        return False
    if flt.check_edit_perm and not (
            (user.can_all or user.can_edit_messages) and bot.can_edit_messages):
        return False
    if flt.check_delete_perm and not (
            (user.can_all or user.can_delete_messages) and bot.can_delete_messages):
        return False
    if flt.check_restrict_perm and not (
            (user.can_all or user.can_restrict_members) and bot.can_restrict_members):
        return False
    if flt.check_promote_perm and not (
            (user.can_all or user.can_promote_members) and bot.can_promote_members):
        return False
    if flt.check_invite_perm and not (
            (user.can_all or user.can_invite_users) and bot.can_invite_users):
        return False
    if flt.check_pin_perm and not (
            (user.can_all or user.can_pin_messages) and bot.can_pin_messages):
        return False
    return True


class RawDecorator(RawClient):
    """ userge raw decoretor """
    _PYRORETTYPE = Callable[[_PYROFUNC], _PYROFUNC]

    def __init__(self, **kwargs) -> None:
        self.manager = types.new.Manager(self)
        self._tasks: List[Callable[[], Any]] = []
        super().__init__(**kwargs)

    def on_filters(self, filters: RawFilter, group: int = 0,
                   **kwargs: Union[bool]) -> 'RawDecorator._PYRORETTYPE':
        """ abstract on filter method """

    def _build_decorator(self,
                         flt: Union['types.raw.Command', 'types.raw.Filter'],
                         **kwargs: Union[str, bool]) -> 'RawDecorator._PYRORETTYPE':
        def decorator(func: _PYROFUNC) -> _PYROFUNC:
            async def template(r_c: Union['_client.Userge', '_client.UsergeBot'],
                               r_m: RawMessage) -> None:
                if Config.DISABLED_ALL and r_m.chat.id != Config.LOG_CHANNEL_ID:
                    return
                if r_m.chat and r_m.chat.id in Config.DISABLED_CHATS:
                    return
                await _init(r_c, r_m)
                _raise = partial(_raise_func, r_c, r_m.chat.id, r_m.message_id)
                if r_m.chat and r_m.chat.type not in flt.scope:
                    if isinstance(flt, types.raw.Command):
                        await _raise(f"`invalid chat type [{r_m.chat.type}]`")
                    return
                if r_m.chat and flt.only_admins and not await _is_admin(r_c, r_m):
                    if isinstance(flt, types.raw.Command):
                        await _raise("`chat admin required`")
                    return
                if r_m.chat and flt.check_perm:
                    is_admin = await _is_admin(r_c, r_m)
                    c_m = _get_chat_member(r_c, r_m)
                    if not c_m:
                        if isinstance(flt, types.raw.Command):
                            await _raise(f"`invalid chat type [{r_m.chat.type}]`")
                        return
                    if c_m.status != "creator":
                        if flt.check_change_info_perm and not c_m.can_change_info:
                            if isinstance(flt, types.raw.Command):
                                await _raise("`required permisson [change_info]`")
                            return
                        if flt.check_edit_perm and not c_m.can_edit_messages:
                            if isinstance(flt, types.raw.Command):
                                await _raise("`required permisson [edit_messages]`")
                            return
                        if flt.check_delete_perm and not c_m.can_delete_messages:
                            if isinstance(flt, types.raw.Command):
                                await _raise("`required permisson [delete_messages]`")
                            return
                        if flt.check_restrict_perm and not c_m.can_restrict_members:
                            if isinstance(flt, types.raw.Command):
                                if is_admin:
                                    await _raise("`required permisson [restrict_members]`")
                                else:
                                    await _raise("`chat admin required`")
                            return
                        if flt.check_promote_perm and not c_m.can_promote_members:
                            if isinstance(flt, types.raw.Command):
                                if is_admin:
                                    await _raise("`required permisson [promote_members]`")
                                else:
                                    await _raise("`chat admin required`")
                            return
                        if flt.check_invite_perm and not c_m.can_invite_users:
                            if isinstance(flt, types.raw.Command):
                                await _raise("`required permisson [invite_users]`")
                            return
                        if flt.check_pin_perm and not c_m.can_pin_messages:
                            if isinstance(flt, types.raw.Command):
                                await _raise("`required permisson [pin_messages]`")
                            return
                if RawClient.DUAL_MODE:
                    if (flt.check_client
                            or (r_m.from_user and r_m.from_user.id in Config.SUDO_USERS)):
                        cond = True
                        async with await _get_lock(str(flt)):
                            if flt.only_admins:
                                cond = cond and await _both_are_admins(r_c, r_m)
                            if flt.check_perm:
                                cond = cond and await _both_have_perm(flt, r_c, r_m)
                            if cond:
                                if Config.USE_USER_FOR_CLIENT_CHECKS:
                                    # pylint: disable=protected-access
                                    if isinstance(r_c, _client.UsergeBot):
                                        return
                                elif await _bot_is_present(r_c, r_m):
                                    if isinstance(r_c, _client.Userge):
                                        return
                if flt.check_downpath and not os.path.isdir(Config.DOWN_PATH):
                    os.makedirs(Config.DOWN_PATH)
                try:
                    await func(types.bound.Message.parse(
                        r_c, r_m, module=func.__module__, **kwargs))
                except (StopPropagation, ContinuePropagation):  # pylint: disable=W0706
                    raise
                except Exception as f_e:  # pylint: disable=broad-except
                    _LOG.exception(_LOG_STR, f_e)
                    await self._channel.log(f"**PLUGIN** : `{func.__module__}`\n"
                                            f"**FUNCTION** : `{func.__name__}`\n"
                                            f"**ERROR** : `{f_e or None}`\n"
                                            f"\n```{format_exc().strip()}```",
                                            "TRACEBACK")
                    await _raise(f"`{f_e}`\n__see logs for more info__")
            flt.update(func, template)
            self.manager.get_plugin(func.__module__).add(flt)
            _LOG.debug(_LOG_STR, f"Imported => [ async def {func.__name__}(message) ] "
                       f"from {func.__module__} {flt}")
            return func
        return decorator
