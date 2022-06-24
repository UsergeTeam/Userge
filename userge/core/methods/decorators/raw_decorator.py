# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['RawDecorator']

import os
import time
import asyncio
from traceback import format_exc
from functools import partial
from typing import List, Dict, Union, Any, Callable, Optional, Awaitable

from pyrogram import StopPropagation, ContinuePropagation, enums
from pyrogram.filters import Filter as RawFilter
from pyrogram.types import Message as RawMessage, ChatMember
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid, UserNotParticipant

from userge import logging, config
from userge.plugins.builtin import sudo, system
from ...ext import RawClient
from ... import types, client as _client  # pylint: disable=unused-import

_LOG = logging.getLogger(__name__)

_PYROFUNC = Callable[['types.bound.Message'], Any]
_TASK_1_START_TO = time.time()
_TASK_2_START_TO = time.time()

_B_CMN_CHT: List[int] = []
_B_AD_CHT: Dict[int, ChatMember] = {}
_B_NM_CHT: Dict[int, ChatMember] = {}

_U_AD_CHT: Dict[int, ChatMember] = {}
_U_NM_CHT: Dict[int, ChatMember] = {}

_CH_LKS: Dict[str, asyncio.Lock] = {}
_CH_LKS_LK = asyncio.Lock()


async def _update_u_cht(r_m: RawMessage) -> Optional[ChatMember]:
    if r_m.chat.id not in {**_U_AD_CHT, **_U_NM_CHT}:
        try:
            user = await r_m.chat.get_member(RawClient.USER_ID)
        except UserNotParticipant:
            return None
        # is this required?
        # user.privileges.can_all = None
        # if user.status == enums.ChatMemberStatus.OWNER:
            # user.privileges.can_all = True
        if user.status in (
                enums.ChatMemberStatus.OWNER,
                enums.ChatMemberStatus.ADMINISTRATOR):
            _U_AD_CHT[r_m.chat.id] = user
        else:
            _U_NM_CHT[r_m.chat.id] = user
    elif r_m.chat.id in _U_AD_CHT:
        user = _U_AD_CHT[r_m.chat.id]
    else:
        user = _U_NM_CHT[r_m.chat.id]
    return user


async def _update_b_cht(r_m: RawMessage) -> Optional[ChatMember]:
    if r_m.chat.id not in {**_B_AD_CHT, **_B_NM_CHT}:
        try:
            bot = await r_m.chat.get_member(RawClient.BOT_ID)
        except UserNotParticipant:
            return None
        if bot.status == enums.ChatMemberStatus.ADMINISTRATOR:
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


async def _init(r_m: RawMessage) -> None:
    if r_m.from_user and (
        r_m.from_user.is_self or (
            r_m.from_user.id in sudo.USERS) or (
                r_m.from_user.id in config.OWNER_ID)):
        RawClient.LAST_OUTGOING_TIME = time.time()


async def _raise_func(r_c: Union['_client.Userge', '_client.UsergeBot'],
                      r_m: RawMessage, text: str) -> None:
    # pylint: disable=protected-access
    if r_m.chat.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
        await r_m.reply(f"< **ERROR**: {text} ! >")
    else:
        await r_c._channel.log(f"{text}\nCaused By: [link]({r_m.link})", "ERROR")


async def _is_admin(r_m: RawMessage, is_bot: bool) -> bool:
    if r_m.chat.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
        return False
    if round(time.time() - _TASK_1_START_TO) > 10:
        _clear_cht()
    if is_bot:
        await _update_b_cht(r_m)
        return r_m.chat.id in _B_AD_CHT
    await _update_u_cht(r_m)
    return r_m.chat.id in _U_AD_CHT


def _get_chat_member(r_m: RawMessage, is_bot: bool) -> Optional[ChatMember]:
    if r_m.chat.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
        return None
    if is_bot:
        if r_m.chat.id in _B_AD_CHT:
            return _B_AD_CHT[r_m.chat.id]
        if r_m.chat.id in _B_NM_CHT:
            return _B_NM_CHT[r_m.chat.id]
    if r_m.chat.id in _U_AD_CHT:
        return _U_AD_CHT[r_m.chat.id]
    if r_m.chat.id in _U_NM_CHT:
        return _U_NM_CHT[r_m.chat.id]
    return None


async def _get_lock(key: str) -> asyncio.Lock:
    async with _CH_LKS_LK:
        if key not in _CH_LKS:
            _CH_LKS[key] = asyncio.Lock()
    return _CH_LKS[key]


async def _bot_is_present(r_c: Union['_client.Userge', '_client.UsergeBot'],
                          r_m: RawMessage, is_bot: bool) -> bool:
    global _TASK_2_START_TO  # pylint: disable=global-statement
    if is_bot:
        if r_m.chat.id not in _B_CMN_CHT:
            _B_CMN_CHT.append(r_m.chat.id)
    else:
        if round(time.time() - _TASK_2_START_TO) > 10:
            try:
                chats = await r_c.get_common_chats(RawClient.BOT_ID)
                _B_CMN_CHT.clear()
                for chat in chats:
                    _B_CMN_CHT.append(chat.id)
            except PeerIdInvalid:
                pass
            _TASK_2_START_TO = time.time()
    return r_m.chat.id in _B_CMN_CHT


async def _both_are_admins(r_c: Union['_client.Userge', '_client.UsergeBot'],
                           r_m: RawMessage, is_bot: bool) -> bool:
    if not await _bot_is_present(r_c, r_m, is_bot):
        return False
    return r_m.chat.id in _B_AD_CHT and r_m.chat.id in _U_AD_CHT


async def _both_have_perm(flt: Union['types.raw.Command', 'types.raw.Filter'],
                          r_c: Union['_client.Userge', '_client.UsergeBot'],
                          r_m: RawMessage, is_bot: bool) -> bool:
    if not await _bot_is_present(r_c, r_m, is_bot):
        return False
    try:
        user = await _update_u_cht(r_m)
        bot = await _update_b_cht(r_m)
    except PeerIdInvalid:
        return False
    if user is None or bot is None:
        return False

    if flt.check_change_info_perm and not (
            (user.privileges and bot.privileges) and (
            user.privileges.can_change_info and bot.privileges.can_change_info)):
        return False
    if flt.check_edit_perm and not ((user.privileges and bot.privileges) and (
            user.privileges.can_edit_messages and bot.privileges.can_edit_messages)):
        return False
    if flt.check_delete_perm and not ((user.privileges and bot.privileges) and (
            user.privileges.can_delete_messages and bot.privileges.can_delete_messages)):
        return False
    if flt.check_restrict_perm and not ((user.privileges and bot.privileges) and (
            user.privileges.can_restrict_members and bot.privileges.can_restrict_members)):
        return False
    if flt.check_promote_perm and not ((user.privileges and bot.privileges) and (
            user.privileges.can_promote_members and bot.privileges.can_promote_members)):
        return False
    if flt.check_invite_perm and not ((user.privileges and bot.privileges) and (
            user.privileges.can_invite_users and bot.privileges.can_invite_users)):
        return False
    if flt.check_pin_perm and not ((user.privileges and bot.privileges) and (
            user.privileges.can_pin_messages and bot.privileges.can_pin_messages)):
        return False
    return True


class RawDecorator(RawClient):
    """ userge raw decorator """
    _PYRORETTYPE = Callable[[_PYROFUNC], _PYROFUNC]

    def __init__(self, **kwargs) -> None:
        self.manager = types.new.Manager(self)
        super().__init__(**kwargs)

    def add_task(self, task: Callable[[], Awaitable[Any]]) -> Callable[[], Awaitable[Any]]:
        """ add a background task which is attached to this plugin. """
        self.manager.get_plugin(task.__module__).add_task(task)
        return task

    def on_start(self, callback: Callable[[], Awaitable[Any]]) -> None:
        """ set a callback to calls when the plugin is loaded """
        self.manager.get_plugin(callback.__module__).set_on_start_callback(callback)

    def on_stop(self, callback: Callable[[], Awaitable[Any]]) -> None:
        """ set a callback to calls when the plugin is unloaded """
        self.manager.get_plugin(callback.__module__).set_on_stop_callback(callback)

    def on_exit(self, callback: Callable[[], Awaitable[Any]]) -> None:
        """ set a callback to calls when the userge is exiting """
        self.manager.get_plugin(callback.__module__).set_on_exit_callback(callback)

    def on_filters(self, filters: RawFilter, group: int = 0,
                   **kwargs: Union[str, bool]) -> 'RawDecorator._PYRORETTYPE':
        """ abstract on filter method """

    def _build_decorator(self,
                         flt: Union['types.raw.Command',
                                    'types.raw.Filter'],
                         **kwargs: Union[str, bool]) -> 'RawDecorator._PYRORETTYPE':
        def decorator(func: _PYROFUNC) -> _PYROFUNC:
            async def template(r_c: Union['_client.Userge', '_client.UsergeBot'],
                               r_m: RawMessage) -> None:
                await self.manager.wait()

                if system.Dynamic.DISABLED_ALL and r_m.chat.id != config.LOG_CHANNEL_ID:
                    raise StopPropagation
                if r_m.chat and r_m.chat.id in system.DISABLED_CHATS:
                    raise StopPropagation
                if config.IGNORE_VERIFIED_CHATS and r_m.from_user and r_m.from_user.is_verified:
                    raise StopPropagation

                await _init(r_m)
                _raise = partial(_raise_func, r_c, r_m)
                if r_m.chat and r_m.chat.type not in flt.scope:
                    if isinstance(flt, types.raw.Command):
                        await _raise(f"`invalid chat type [{r_m.chat.type.name}]`")
                    return
                is_bot = r_c.is_bot
                if r_m.chat and flt.only_admins and not await _is_admin(r_m, is_bot):
                    if isinstance(flt, types.raw.Command):
                        await _raise("`chat admin required`")
                    return
                if r_m.chat and flt.check_perm:
                    is_admin = await _is_admin(r_m, is_bot)
                    c_m = _get_chat_member(r_m, is_bot)
                    if not c_m:
                        if isinstance(flt, types.raw.Command):
                            await _raise(f"`invalid chat type [{r_m.chat.type.name}]`")
                        return
                    if c_m.status != enums.ChatMemberStatus.OWNER:
                        if flt.check_change_info_perm and not (
                                c_m.privileges and c_m.privileges.can_change_info):
                            if isinstance(flt, types.raw.Command):
                                await _raise("`required permission [change_info]`")
                            return
                        if flt.check_edit_perm and not (
                                c_m.privileges and c_m.privileges.can_edit_messages):
                            if isinstance(flt, types.raw.Command):
                                await _raise("`required permission [edit_messages]`")
                            return
                        if flt.check_delete_perm and not (
                                c_m.privileges and c_m.privileges.can_delete_messages):
                            if isinstance(flt, types.raw.Command):
                                await _raise("`required permission [delete_messages]`")
                            return
                        if flt.check_restrict_perm and not (
                                c_m.privileges and c_m.privileges.can_restrict_members):
                            if isinstance(flt, types.raw.Command):
                                if is_admin:
                                    await _raise("`required permission [restrict_members]`")
                                else:
                                    await _raise("`chat admin required`")
                            return
                        if flt.check_promote_perm and not (
                                c_m.privileges and c_m.privileges.can_promote_members):
                            if isinstance(flt, types.raw.Command):
                                if is_admin:
                                    await _raise("`required permission [promote_members]`")
                                else:
                                    await _raise("`chat admin required`")
                            return
                        if flt.check_invite_perm and not (
                                c_m.privileges and c_m.privileges.can_invite_users):
                            if isinstance(flt, types.raw.Command):
                                await _raise("`required permission [invite_users]`")
                            return
                        if flt.check_pin_perm and not (
                                c_m.privileges and c_m.privileges.can_pin_messages):
                            if isinstance(flt, types.raw.Command):
                                await _raise("`required permission [pin_messages]`")
                            return

                if RawClient.DUAL_MODE and (
                    flt.check_client or (
                        r_m.from_user and r_m.from_user.id != RawClient.USER_ID
                        and (r_m.from_user.id in config.OWNER_ID
                             or r_m.from_user.id in sudo.USERS))):
                    cond = True
                    async with await _get_lock(str(flt)):
                        if flt.only_admins:
                            cond = cond and await _both_are_admins(r_c, r_m, is_bot)
                        if flt.check_perm:
                            cond = cond and await _both_have_perm(flt, r_c, r_m, is_bot)
                        if cond:
                            if config.Dynamic.USER_IS_PREFERRED:
                                if isinstance(r_c, _client.UsergeBot):
                                    return
                            elif await _bot_is_present(r_c, r_m, is_bot) and isinstance(
                                    r_c, _client.Userge):
                                return

                if flt.check_downpath and not os.path.isdir(
                        config.Dynamic.DOWN_PATH):
                    os.makedirs(config.Dynamic.DOWN_PATH)

                try:
                    await func(types.bound.Message.parse(
                        r_c, r_m, module=module, **kwargs))
                except (StopPropagation, ContinuePropagation):  # pylint: disable=W0706
                    raise
                except Exception as f_e:  # pylint: disable=broad-except
                    _LOG.exception(f_e)
                    await self._channel.log(f"**PLUGIN** : `{module}`\n"
                                            f"**FUNCTION** : `{func.__name__}`\n"
                                            f"**ERROR** : `{f_e or None}`\n"
                                            f"\n```{format_exc().strip()}```",
                                            "TRACEBACK")
                finally:
                    if flt.propagate:
                        raise ContinuePropagation
                    if flt.propagate is not None:
                        raise StopPropagation

            module = func.__module__

            flt.update(func, template)
            self.manager.get_plugin(module).add(flt)

            return func
        return decorator
