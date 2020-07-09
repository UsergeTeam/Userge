# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Command']

from typing import Union, Dict, List, Optional, Callable, Any

from pyrogram.client.handlers.handler import Handler

from userge import Config, logging
from .filter import Filter
from ... import client as _client  # pylint: disable=unused-import

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  [[[[[  %s  ]]]]]  !>>>"


class Command(Filter):
    """ command class """
    def __init__(self,  # pylint: disable=super-init-not-called
                 client: '_client.Userge',
                 name: str,
                 about: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]],
                 group: int,
                 allow_via_bot: bool) -> None:
        self._client = client
        self.name = name
        self.about = _format_about(about)
        self._group = group
        self._allow_via_bot = allow_via_bot
        self._enabled = True
        self._loaded = False
        self._handler: Handler
        self.doc: Optional[str]
        _LOG.debug(_LOG_STR, f"created command -> {self.name}")

    def __repr__(self) -> str:
        return f"<command - {self.name}>"

    def update(self, func: Callable[[Any], Any], handler: Handler) -> None:
        """ update command """
        self._handler = handler
        self.doc = func.__doc__.strip() if func.__doc__ else None
        _LOG.debug(_LOG_STR, f"created command -> {self.name}")


def _format_about(about: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]]) -> str:
    if isinstance(about, dict):
        tmp_chelp = ''
        if 'header' in about and isinstance(about['header'], str):
            tmp_chelp += f"<i><b>{about['header'].title()}</b><i>"
            del about['header']
        if 'description' in about and isinstance(about['description'], str):
            tmp_chelp += ("\n\n📝 <u><b>Description</b></u> :\n\n    "
                          f"<i>{about['description'].capitalize()}</i>")
            del about['description']
        if 'flags' in about:
            tmp_chelp += "\n\n⛓ <u><b>Available Flags</b></u> :\n"
            if isinstance(about['flags'], dict):
                for f_n, f_d in about['flags'].items():
                    tmp_chelp += f"\n    ▫ <code>{f_n}</code> : <i>{f_d.lower()}</i>"
            else:
                tmp_chelp += f"\n    {about['flags']}"
            del about['flags']
        if 'options' in about:
            tmp_chelp += "\n\n🕶 <u><b>Available Options</b></u> :\n"
            if isinstance(about['options'], dict):
                for o_n, o_d in about['options'].items():
                    tmp_chelp += f"\n    ▫ <code>{o_n}</code> : <i>{o_d.lower()}</i>"
            else:
                tmp_chelp += f"\n    {about['options']}"
            del about['options']
        if 'types' in about:
            tmp_chelp += "\n\n🎨 <u><b>Supported Types</b></u> :\n\n"
            if isinstance(about['types'], list):
                for _opt in about['types']:
                    tmp_chelp += f"    <code>{_opt}</code> ,"
            else:
                tmp_chelp += f"    {about['types']}"
            del about['types']
        if 'usage' in about:
            tmp_chelp += f"\n\n✒ <u><b>Usage</b></u> :\n\n<code>{about['usage']}</code>"
            del about['usage']
        if 'examples' in about:
            tmp_chelp += "\n\n✏ <u><b>Examples</b></u> :"
            if isinstance(about['examples'], list):
                for ex_ in about['examples']:
                    tmp_chelp += f"\n\n    <code>{ex_}</code>"
            else:
                tmp_chelp += f"\n\n    <code>{about['examples']}</code>"
            del about['examples']
        if 'others' in about:
            tmp_chelp += f"\n\n📎 <u><b>Others</b></u> :\n\n{about['others']}"
            del about['others']
        if about:
            for t_n, t_d in about.items():
                tmp_chelp += f"\n\n⚙ <u><b>{t_n.title()}</b></u> :\n"
                if isinstance(t_d, dict):
                    for o_n, o_d in t_d.items():
                        tmp_chelp += f"\n    ▫ <code>{o_n}</code> : <i>{o_d.lower()}</i>"
                elif isinstance(t_d, list):
                    tmp_chelp += '\n'
                    for _opt in t_d:
                        tmp_chelp += f"    <code>{_opt}</code> ,"
                else:
                    tmp_chelp += '\n'
                    tmp_chelp += t_d
        chelp = tmp_chelp.replace('{tr}', Config.CMD_TRIGGER)
        del tmp_chelp
        return chelp
    return about
