# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Userge']

import re
import os
import sys
import asyncio
import importlib
from types import ModuleType
from typing import (
    Dict, List, Tuple, Optional, Union, Any, Callable)

import psutil
import nest_asyncio
from pyrogram import (
    Client as RawClient, Message as RawMessage,
    Filters, MessageHandler, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply)
from pyrogram.client.handlers.handler import Handler
from pyrogram.api import functions

from userge import logging, Config
from userge.plugins import get_all_plugins
from .message import Message
from .ext import CLogger, Conv

_PYROFUNC = Callable[[Message], Any]

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  #####  %s  #####  !>>>"


class Userge(RawClient):
    """Userge, the userbot"""
    def __init__(self) -> None:
        self._help_dict: Dict[str, Dict[str, str]] = {}
        self._handlers: Dict[str, List[Tuple[Handler, int]]] = {}
        self._imported: List[ModuleType] = []
        self._tasks: List[Callable[[Any], Any]] = []
        self._channel = self.getCLogger(__name__)
        _LOG.info(_LOG_STR, "Setting Userge Configs")
        super().__init__(Config.HU_STRING_SESSION,
                         api_id=Config.API_ID,
                         api_hash=Config.API_HASH)

    @staticmethod
    def getLogger(name: str) -> logging.Logger:
        """This returns new logger object"""
        _LOG.debug(_LOG_STR, f"Creating Logger => {name}")
        return logging.getLogger(name)

    def getCLogger(self, name: str) -> CLogger:
        """This returns new channel logger object"""
        _LOG.debug(_LOG_STR, f"Creating CLogger => {name}")
        return CLogger(self, name)

    def conversation(self,
                     chat_id: Union[str, int],
                     *, timeout: Union[int, float] = 10,
                     limit: int = 10) -> Conv:
        """\nThis returns new conversation object.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages)
                you can simply use "me" or "self".
                For a contact that exists in your Telegram address book
                you can use his phone number (str).

            timeout (``int`` | ``float`` | , *optional*):
                set conversation timeout.
                defaults to 10.

            limit (``int`` | , *optional*):
                set conversation message limit.
                defaults to 10.
        """
        return Conv(self, chat_id, timeout, limit)

    async def send_read_acknowledge(self,
                                    chat_id: Union[int, str],
                                    message: Union[List[RawMessage],
                                                   Optional[RawMessage]] = None,
                                    *, max_id: Optional[int] = None,
                                    clear_mentions: bool = False) -> bool:
        """\nMarks messages as read and optionally clears mentions.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages)
                you can simply use "me" or "self".
                For a contact that exists in your Telegram address book
                you can use his phone number (str).

            message (``list`` | :obj: `Message`, *optional*):
                Either a list of messages or a single message.

            max_id (``int``, *optional*):
                Until which message should the read acknowledge be sent for.
                This has priority over the ``message`` parameter.

            clear_mentions (``bool``, *optional*):
                Whether the mention badge should be cleared (so that
                there are no more mentions) or not for the given entity.
                If no message is provided, this will be the only action
                taken.
                defaults to False.

        Returns:
            On success, True is returned.
        """
        if max_id is None:
            if message:
                if isinstance(message, list):
                    max_id = max(msg.message_id for msg in message)
                else:
                    max_id = message.message_id
            else:
                max_id = 0
        if clear_mentions:
            await self.send(
                functions.messages.ReadMentions(
                    peer=await self.resolve_peer(chat_id)))
            if max_id is None:
                return True
        if max_id is not None:
            return await self.read_history(chat_id=chat_id, max_id=max_id)
        return False

    async def get_user_dict(self, user_id: Union[int, str]) -> Dict[str, str]:
        """This will return user `Dict` which contains
        `id`(chat id), `fname`(first name), `lname`(last name),
        `flname`(full name), `uname`(username) and `mention`.
        """
        user_obj = await self.get_users(user_id)
        fname = (user_obj.first_name or '').strip()
        lname = (user_obj.last_name or '').strip()
        username = (user_obj.username or '').strip()
        if fname and lname:
            full_name = fname + ' ' + lname
        elif fname or lname:
            full_name = fname or lname
        else:
            full_name = "user"
        mention = f"[{username or full_name}](tg://user?id={user_id})"
        return {'id': user_obj.id, 'fname': fname, 'lname': lname,
                'flname': full_name, 'uname': username, 'mention': mention}

    async def send_message(self,
                           chat_id: Union[int, str],
                           text: str,
                           del_in: int = -1,
                           log: Union[bool, str] = False,
                           parse_mode: Union[str, object] = object,
                           disable_web_page_preview: Optional[bool] = None,
                           disable_notification: Optional[bool] = None,
                           reply_to_message_id: Optional[int] = None,
                           schedule_date: Optional[int] = None,
                           reply_markup: Union[InlineKeyboardMarkup,
                                               ReplyKeyboardMarkup,
                                               ReplyKeyboardRemove,
                                               ForceReply] = None) -> Union[Message, bool]:
        """\nSend text messages.

        Example:
                @userge.send_message(chat_id=12345, text='test')

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages)
                you can simply use "me" or "self".
                For a contact that exists in your Telegram address book
                you can use his phone number (str).

            text (``str``):
                Text of the message to be sent.

            del_in (``int``):
                Time in Seconds for delete that message.

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded to the log channel.
                If ``str``, the logger name will be updated.

            parse_mode (``str``, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            schedule_date (``int``, *optional*):
                Date when the message will be automatically sent. Unix time.

            reply_markup (:obj:`InlineKeyboardMarkup` | :obj:`ReplyKeyboardMarkup`
            | :obj:`ReplyKeyboardRemove` | :obj:`ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard,
                custom reply keyboard, instructions to remove
                reply keyboard or to force a reply from the user.

        Returns:
            :obj:`Message`: On success, the sent text message or True is returned.
        """
        msg = await super().send_message(chat_id=chat_id,
                                         text=text,
                                         parse_mode=parse_mode,
                                         disable_web_page_preview=disable_web_page_preview,
                                         disable_notification=disable_notification,
                                         reply_to_message_id=reply_to_message_id,
                                         schedule_date=schedule_date,
                                         reply_markup=reply_markup)
        if log:
            if isinstance(log, str):
                self._channel.update(log)
            await self._channel.fwd_msg(msg)
        del_in = del_in or Config.MSG_DELETE_TIMEOUT
        if del_in > 0:
            await asyncio.sleep(del_in)
            return await msg.delete()
        return Message(self, msg)

    def on_cmd(self,
               command: str,
               about: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]],
               group: int = 0,
               name: str = '',
               trigger: str = Config.CMD_TRIGGER,
               filter_me: bool = True,
               **kwargs: Union[str, bool, Dict[str, Union[str, List[str], Dict[str, str]]]]
               ) -> Callable[[_PYROFUNC], _PYROFUNC]:
        """\nDecorator for handling messages.

        Example:
                @userge.on_cmd('test', about='for testing')

        Parameters:
            command (``str``):
                command name to execute (without trigger!).

            about (``str`` | ``dict``):
                help string or dict for command.
                {
                    'header': ``str``,
                    'description': ``str``,
                    'flags': ``str`` | ``dict``,
                    'options': ``str`` | ``dict``,
                    'types': ``str`` | ``list``,
                    'usage': ``str``,
                    'examples': ``str`` | ``list``,
                    'others': ``str``,
                    'any_title': ``str`` | ``list`` | ``dict``
                }

            group (``int``, *optional*):
                The group identifier, defaults to 0.

            name (``str``, *optional*):
                name for command.

            trigger (``str``, *optional*):
                trigger to start command, defaults to '.'.

            filter_me (``bool``, *optional*):
                If ``True``, Filters.me = True,  defaults to True.

            kwargs:
                prefix (``str``, *optional*):
                    set prefix for flags, defaults to '-'.

                del_pre (``bool``, *optional*):
                    If ``True``, flags returns without prefix,
                    defaults to False.
        """
        pattern = f"^(?:\\{trigger}|\\{Config.SUDO_TRIGGER}){command.lstrip('^')}" if trigger \
            else f"^{command.lstrip('^')}"
        if [i for i in '^()[]+*.\\|?:$' if i in command]:
            match = re.match("(\\w[\\w_]*)", command)
            cname = match.groups()[0] if match else ''
            cname = name or cname
            cname = trigger + cname if cname else ''
        else:
            cname = trigger + command
            cname = name or cname
            pattern += r"(?:\s([\S\s]+))?$"
        kwargs.update({'cname': cname, 'chelp': about})

        filters_ = Filters.regex(pattern=pattern)
        filter_my_trigger = Filters.create(lambda _, query: \
            query.text.startswith(trigger) if trigger else True)
        sudo_filter = Filters.create(lambda _, query: \
            (query.from_user
             and query.from_user.id in Config.SUDO_USERS
             and (query.text.startswith(Config.SUDO_TRIGGER) if trigger else True)))
        sudo_cmd_filter = Filters.create(lambda _, __: \
            cname.lstrip(trigger) in Config.ALLOWED_COMMANDS)
        if filter_me:
            filters_ = (filters_
                        & (((Filters.outgoing | Filters.me) & filter_my_trigger)
                           | (Filters.incoming & sudo_filter & sudo_cmd_filter)))
        return self._build_decorator(log=f"On {pattern}", filters=filters_,
                                     group=group, **kwargs)

    def on_filters(self,
                   filters: Filters,
                   group: int = 0) -> Callable[[_PYROFUNC], _PYROFUNC]:
        """Decorator for handling filters"""
        return self._build_decorator(log=f"On Filters {filters}",
                                     filters=filters, group=group)

    def on_new_member(self,
                      welcome_chats: Filters.chat,
                      group: int = -2) -> Callable[[_PYROFUNC], _PYROFUNC]:
        """Decorator for handling new members"""
        return self._build_decorator(log=f"On New Member in {welcome_chats}",
                                     filters=Filters.new_chat_members & welcome_chats,
                                     group=group)

    def on_left_member(self,
                       leaving_chats: Filters.chat,
                       group: int = -2) -> Callable[[_PYROFUNC], _PYROFUNC]:
        """Decorator for handling left members"""
        return self._build_decorator(log=f"On Left Member in {leaving_chats}",
                                     filters=Filters.left_chat_member & leaving_chats,
                                     group=group)

    def add_task(self, func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """add tasks"""
        self._tasks.append(func)
        return func

    def get_help(self,
                 key: str = '',
                 all_cmds: bool = False) -> Tuple[Union[str, List[str]], Union[bool, str]]:
        """This will return help string for specific key
        or all modules or commands as `List`.
        """
        if not key and not all_cmds:
            return sorted(list(self._help_dict)), True         # names of all modules
        if (not key.startswith(Config.CMD_TRIGGER)
                and key in self._help_dict
                and (len(self._help_dict[key]) > 1
                     or list(self._help_dict[key])[0].lstrip(Config.CMD_TRIGGER) != key)):
            return sorted(list(self._help_dict[key])), False   # all commands for that module

        dict_ = {x: y for _, i in self._help_dict.items() for x, y in i.items()}
        if all_cmds:
            return sorted(list(dict_)), False                   # all commands for .s
        key = key.lstrip(Config.CMD_TRIGGER)
        key_ = Config.CMD_TRIGGER + key
        if key in dict_:
            return dict_[key], key      # help text and command for given command
        if key_ in dict_:
            return dict_[key_], key_    # help text and command for modified command
        return '', False                # if unknown

    def _add_help(self,
                  module: str,
                  cname: str = '',
                  chelp: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]] = '',
                  **_: Union[str, bool]) -> None:
        if cname:
            _LOG.debug(_LOG_STR, f"Updating Help Dict => [ {cname} : {chelp} ]")
            mname = module.split('.')[-1]
            if isinstance(chelp, dict):
                tmp_chelp = ''
                if 'header' in chelp and isinstance(chelp['header'], str):
                    tmp_chelp += f"__**{chelp['header'].title()}**__"
                    del chelp['header']
                if 'description' in chelp and isinstance(chelp['description'], str):
                    tmp_chelp += ("\n\n📝 --**Description**-- :\n\n    "
                                  f"__{chelp['description'].capitalize()}__")
                    del chelp['description']
                if 'flags' in chelp:
                    tmp_chelp += f"\n\n⛓ --**Available Flags**-- :\n"
                    if isinstance(chelp['flags'], dict):
                        for f_n, f_d in chelp['flags'].items():
                            tmp_chelp += f"\n    ▫ `{f_n}` : __{f_d.lower()}__"
                    else:
                        tmp_chelp += f"\n    {chelp['flags']}"
                    del chelp['flags']
                if 'options' in chelp:
                    tmp_chelp += f"\n\n🕶 --**Available Options**-- :\n"
                    if isinstance(chelp['options'], dict):
                        for o_n, o_d in chelp['options'].items():
                            tmp_chelp += f"\n    ▫ `{o_n}` : __{o_d.lower()}__"
                    else:
                        tmp_chelp += f"\n    {chelp['options']}"
                    del chelp['options']
                if 'types' in chelp:
                    tmp_chelp += f"\n\n🎨 --**Supported Types**-- :\n\n"
                    if isinstance(chelp['types'], list):
                        for _opt in chelp['types']:
                            tmp_chelp += f"    `{_opt}` ,"
                    else:
                        tmp_chelp += f"    {chelp['types']}"
                    del chelp['types']
                if 'usage' in chelp:
                    tmp_chelp += f"\n\n✒ --**Usage**-- :\n\n`{chelp['usage']}`"
                    del chelp['usage']
                if 'examples' in chelp:
                    tmp_chelp += f"\n\n✏ --**Examples**-- :\n"
                    if isinstance(chelp['examples'], list):
                        for ex_ in chelp['examples']:
                            tmp_chelp += f"\n    `{ex_}`\n"
                    else:
                        tmp_chelp += f"\n    `{chelp['examples']}`"
                    del chelp['examples']
                if 'others' in chelp:
                    tmp_chelp += f"\n\n📎 --**Others**-- :\n\n{chelp['others']}"
                    del chelp['others']
                if chelp:
                    for t_n, t_d in chelp.items():
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
            if mname in self._help_dict:
                self._help_dict[mname].update({cname: chelp})
            else:
                self._help_dict.update({mname: {cname: chelp}})

    def _add_handler(self, module: str, handler: Handler, group: int) -> None:
        mname = module.split('.')[-1]
        if mname in self._handlers:
            self._handlers[mname].append((handler, group))
        else:
            self._handlers[mname] = [(handler, group)]
        self.add_handler(handler, group)

    def _build_decorator(self,
                         log: str,
                         filters: Filters,
                         group: int,
                         **kwargs: Union[str, bool,
                                         Dict[str, Union[str, List[str], Dict[str, str]]]]
                         ) -> Callable[[_PYROFUNC], _PYROFUNC]:
        def _decorator(func: _PYROFUNC) -> _PYROFUNC:
            async def _template(_: RawClient, __: RawMessage) -> None:
                await func(Message(_, __, **kwargs))
            _LOG.debug(_LOG_STR, f"Loading => [ async def {func.__name__}(message) ] " + \
                f"from {func.__module__} `{log}`")
            self._add_help(func.__module__, **kwargs)
            self._add_handler(func.__module__, MessageHandler(_template, filters), group)
            return func
        return _decorator

    def load_plugin(self, name: str) -> None:
        """Load plugin to Userge"""
        _LOG.debug(_LOG_STR, f"Importing {name}")
        self._imported.append(
            importlib.import_module(f"userge.plugins.{name}"))
        _LOG.debug(_LOG_STR, f"Imported {self._imported[-1].__name__} Plugin Successfully")

    def unload_plugin(self, module: str) -> Optional[List[str]]:
        """unload plugin from userge"""
        if module not in self._handlers:
            return None
        for handler_, group_ in self._handlers[module]:
            self.remove_handler(handler_, group_)
        return list(self._help_dict.pop(module))

    def load_plugins(self) -> None:
        """Load all Plugins"""
        self._imported.clear()
        _LOG.info(_LOG_STR, "Importing All Plugins")
        for name in get_all_plugins():
            try:
                self.load_plugin(name)
            except ImportError as i_e:
                _LOG.error(_LOG_STR, i_e)
        _LOG.info(_LOG_STR, f"Imported ({len(self._imported)}) Plugins => " + \
            str([i.__name__ for i in self._imported]))

    async def reload_plugins(self) -> int:
        """Reload all Plugins"""
        self._help_dict.clear()
        reloaded: List[str] = []
        _LOG.info(_LOG_STR, "Reloading All Plugins")
        for imported in self._imported:
            try:
                reloaded_ = importlib.reload(imported)
            except ImportError as i_e:
                _LOG.error(_LOG_STR, i_e)
            else:
                reloaded.append(reloaded_.__name__)
        _LOG.info(_LOG_STR, f"Reloaded {len(reloaded)} Plugins => {reloaded}")
        return len(reloaded)

    async def restart(self, update_req: bool = False) -> None:
        """Restart the Userge"""
        _LOG.info(_LOG_STR, "Restarting Userge")
        await self.stop()
        try:
            c_p = psutil.Process(os.getpid())
            for handler in c_p.open_files() + c_p.connections():
                os.close(handler.fd)
        except Exception as c_e:
            _LOG.error(_LOG_STR, c_e)
        if update_req:
            os.system("pip3 install -r requirements.txt")
        os.execl(sys.executable, sys.executable, '-m', 'userge')
        sys.exit()

    def begin(self) -> None:
        """This will start the Userge"""
        nest_asyncio.apply()
        Conv.init(self)
        loop = asyncio.get_event_loop()
        run = loop.run_until_complete
        _LOG.info(_LOG_STR, "Starting Userge")
        run(self.start())
        running_tasks: List[asyncio.Task] = []
        for task in self._tasks:
            running_tasks.append(loop.create_task(task()))
        _LOG.info(_LOG_STR, "Idling Userge")
        run(Userge.idle())
        _LOG.info(_LOG_STR, "Exiting Userge")
        for task in running_tasks:
            task.cancel()
        run(self.stop())
        for task in asyncio.all_tasks():
            task.cancel()
        run(loop.shutdown_asyncgens())
        loop.close()
