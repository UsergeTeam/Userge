# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Command']

import re
from typing import Union, Dict, List, Callable

from pyrogram import filters, enums
from pyrogram.types import Message

from userge import config
from userge.plugins.builtin import sudo
from .filter import Filter
from ... import client as _client  # pylint: disable=unused-import


class Command(Filter):
    """ command class """
    def __init__(self, about: str, trigger: str, pattern: str,
                 **kwargs: Union['_client.Userge', int, str, bool]) -> None:
        self.about = about
        self.trigger = trigger
        self.pattern = pattern
        super().__init__(**Filter._parse(**kwargs))  # pylint: disable=protected-access

    @classmethod
    def parse(cls, command: str,  # pylint: disable=arguments-differ
              about: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]],
              trigger: str, name: str, filter_me: bool,
              **kwargs: Union['_client.Userge', int, bool]) -> 'Command':
        """ parse command """
        pattern = '^'
        if trigger:
            pattern += f"(?:\\{trigger}|\\{config.SUDO_TRIGGER}|\\{config.CMD_TRIGGER})"
        pattern += command.lstrip('^')

        if _has_regex(command):
            if name:
                name = trigger + name
            else:
                match = re.match("(\\w[\\w_]*)", command)
                if match:
                    name = trigger + match.groups()[0]
        else:
            if not name:
                name = trigger + command
            pattern += r"(?:\s([\S\s]+))?$"

        filters_ = filters.regex(pattern=pattern)
        if filter_me:
            filters_ &= _outgoing_flt(trigger, name) | _incoming_flt(trigger, name)
        else:
            filters_ &= _public_flt(trigger, name)

        return cls(_format_about(about), trigger, pattern, filters=filters_, name=name, **kwargs)

    def __repr__(self) -> str:
        return f"<command {self.name}>"


def _has_regex(command: str) -> bool:
    return any(map(command.__contains__, '^()[]+*.\\|?:$'))


def _outgoing_flt(trigger: str, name: str) -> filters.Filter:
    return _build_filter(_outgoing_logic, trigger, name)


def _incoming_flt(trigger: str, name: str) -> filters.Filter:
    return _build_filter(_incoming_logic, trigger, name)


def _public_flt(trigger: str, name: str) -> filters.Filter:
    return _build_filter(_public_logic, trigger, name)


def _build_filter(logic: Callable[[Message, str, str], bool],
                  trigger: str, name: str) -> filters.Filter:
    return filters.create(
        lambda _, __, m:
        m.via_bot is None and not m.scheduled
        and not (m.forward_from or m.forward_sender_name)
        and m.text and not m.edit_date and logic(m, trigger, name)
    )


def _outgoing_logic(m: Message, trigger: str, _) -> bool:
    return (
        not (m.from_user and m.from_user.is_bot)
        and (m.outgoing or m.from_user and m.from_user.is_self)
        and not (m.chat and m.chat.type == enums.ChatType.CHANNEL and m.edit_date)
        and (m.text.startswith(trigger) if trigger else True)
    )


def _incoming_logic(m: Message, trigger: str, name: str) -> bool:
    return (
        not m.outgoing and trigger and m.from_user
        and (
            m.from_user.id in config.OWNER_ID or (
                sudo.Dynamic.ENABLED and m.from_user.id in sudo.USERS
                and name.lstrip(trigger) in sudo.COMMANDS
            )
        )
        and m.text.startswith(config.SUDO_TRIGGER)
    )


def _public_logic(m: Message, trigger: str, _) -> bool:
    return (
        True
        if not trigger
        else m.text.startswith(config.CMD_TRIGGER)
        if m.from_user and m.from_user.id in config.OWNER_ID
        else m.text.startswith(config.SUDO_TRIGGER)
        if sudo.Dynamic.ENABLED and m.from_user and m.from_user.id in sudo.USERS
        else m.text.startswith(trigger)
    )


def _format_about(about: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]]) -> str:
    if not isinstance(about, dict):
        return about

    tmp_chelp = ''

    if 'header' in about and isinstance(about['header'], str):
        tmp_chelp += f"{about['header'].capitalize()}"
        del about['header']

    if 'description' in about and isinstance(about['description'], str):
        tmp_chelp += f"\n\n<i>{about['description'].capitalize()}</i>"
        del about['description']

    if 'flags' in about:
        tmp_chelp += "\n\n<b>flags</b>:"

        if isinstance(about['flags'], dict):
            for f_n, f_d in about['flags'].items():
                tmp_chelp += f"\n  <code>{f_n}</code>: <i>{f_d.lower()}</i>"
        else:
            tmp_chelp += f"\n  {about['flags']}"

        del about['flags']

    if 'options' in about:
        tmp_chelp += "\n\n<b>options</b>:"

        if isinstance(about['options'], dict):
            for o_n, o_d in about['options'].items():
                tmp_chelp += f"\n  <code>{o_n}</code>: <i>{o_d.lower()}</i>"
        else:
            tmp_chelp += f"\n  {about['options']}"

        del about['options']

    if 'types' in about:
        tmp_chelp += "\n\n<b>types</b>:\n"

        if isinstance(about['types'], list):
            for _opt in about['types']:
                tmp_chelp += f"  <code>{_opt}</code>,"
        else:
            tmp_chelp += f"  {about['types']}"

        del about['types']

    if 'usage' in about:
        tmp_chelp += f"\n\n<b>usage</b>:\n<code>{about['usage']}</code>"
        del about['usage']

    if 'examples' in about:
        tmp_chelp += "\n\n<b>examples</b>:"

        if isinstance(about['examples'], list):
            for ex_ in about['examples']:
                tmp_chelp += f"\n  <code>{ex_}</code>"
        else:
            tmp_chelp += f"\n  <code>{about['examples']}</code>"

        del about['examples']

    if 'others' in about:
        tmp_chelp += f"\n\n<b>others</b>:\n{about['others']}"
        del about['others']

    if about:
        for t_n, t_d in about.items():
            tmp_chelp += f"\n\n<b>{t_n.lower()}</b>:"

            if isinstance(t_d, dict):
                for o_n, o_d in t_d.items():
                    tmp_chelp += f"\n  <code>{o_n}</code>: <i>{o_d.lower()}</i>"
            elif isinstance(t_d, list):
                tmp_chelp += '\n'
                for _opt in t_d:
                    tmp_chelp += f"  <code>{_opt}</code>,"
            else:
                tmp_chelp += '\n'
                tmp_chelp += t_d

    return tmp_chelp.replace('{tr}', config.CMD_TRIGGER)
