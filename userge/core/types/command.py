# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Command']

from typing import Union, Dict, List

from pyrogram.client.handlers.handler import Handler

from userge import Config, logging
from .filtr import Filtr
from .. import client as _client

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  [[[[[  %s  ]]]]]  !>>>"


class Command(Filtr):
    """command class"""
    def __init__(self,
                 client: '_client.Userge',
                 name: str,
                 about: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]],
                 group: int
                 ) -> None:
        self._client = client
        self.name = name
        self.about = _format_about(about)
        self._group = group
        self._enabled = True
        self._loaded = False
        self._handler: Handler
        self.doc: str
        _LOG.debug(_LOG_STR, f"created command -> {self.name}")

    def __repr__(self) -> str:
        return f"<command - {self.name}>"

    def update_command(self, handler: Handler, doc: str) -> None:
        """update handler and doc in command"""
        self._handler = handler
        self.doc = doc


def _format_about(about: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]]) -> str:
    if isinstance(about, dict):
        tmp_chelp = ''
        if 'header' in about and isinstance(about['header'], str):
            tmp_chelp += f"__**{about['header'].title()}**__"
            del about['header']
        if 'description' in about and isinstance(about['description'], str):
            tmp_chelp += ("\n\n📝 --**Description**-- :\n\n    "
                          f"__{about['description'].capitalize()}__")
            del about['description']
        if 'flags' in about:
            tmp_chelp += "\n\n⛓ --**Available Flags**-- :\n"
            if isinstance(about['flags'], dict):
                for f_n, f_d in about['flags'].items():
                    tmp_chelp += f"\n    ▫ `{f_n}` : __{f_d.lower()}__"
            else:
                tmp_chelp += f"\n    {about['flags']}"
            del about['flags']
        if 'options' in about:
            tmp_chelp += "\n\n🕶 --**Available Options**-- :\n"
            if isinstance(about['options'], dict):
                for o_n, o_d in about['options'].items():
                    tmp_chelp += f"\n    ▫ `{o_n}` : __{o_d.lower()}__"
            else:
                tmp_chelp += f"\n    {about['options']}"
            del about['options']
        if 'types' in about:
            tmp_chelp += "\n\n🎨 --**Supported Types**-- :\n\n"
            if isinstance(about['types'], list):
                for _opt in about['types']:
                    tmp_chelp += f"    `{_opt}` ,"
            else:
                tmp_chelp += f"    {about['types']}"
            del about['types']
        if 'usage' in about:
            tmp_chelp += f"\n\n✒ --**Usage**-- :\n\n`{about['usage']}`"
            del about['usage']
        if 'examples' in about:
            tmp_chelp += "\n\n✏ --**Examples**-- :"
            if isinstance(about['examples'], list):
                for ex_ in about['examples']:
                    tmp_chelp += f"\n\n    `{ex_}`"
            else:
                tmp_chelp += f"\n\n    `{about['examples']}`"
            del about['examples']
        if 'others' in about:
            tmp_chelp += f"\n\n📎 --**Others**-- :\n\n{about['others']}"
            del about['others']
        if about:
            for t_n, t_d in about.items():
                tmp_chelp += f"\n\n⚙ --**{t_n.title()}**-- :\n"
                if isinstance(t_d, dict):
                    for o_n, o_d in t_d.items():
                        tmp_chelp += f"\n    ▫ `{o_n}` : __{o_d.lower()}__"
                elif isinstance(t_d, list):
                    tmp_chelp += '\n'
                    for _opt in t_d:
                        tmp_chelp += f"    `{_opt}` ,"
                else:
                    tmp_chelp += '\n'
                    tmp_chelp += t_d
        chelp = tmp_chelp.replace('{tr}', Config.CMD_TRIGGER)
        del tmp_chelp
        return chelp
    return about
