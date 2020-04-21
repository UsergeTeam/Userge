# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import re
import os
import sys
import asyncio
import importlib
from types import ModuleType
from typing import (
    Dict, List, Tuple, Optional, Union, Any, Callable)
from concurrent.futures import ThreadPoolExecutor

import psutil
import nest_asyncio
from pyrogram import (
    Client as RawClient, Message as RawMessage,
    Filters, MessageHandler, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply)

from userge import logging, Config
from userge.plugins import get_all_plugins
from .message import Message
from .logger import CLogger

PYROFUNC = Callable[[Message], Any]

LOG = logging.getLogger(__name__)
LOG_STR = "<<<!  #####  ___%s___  #####  !>>>"


class Userge(RawClient):
    """
    Userge: userbot
    """

    def __init__(self) -> None:

        self.__help_dict: Dict[str, Dict[str, str]] = {}
        self.__imported: List[ModuleType] = []

        LOG.info(LOG_STR, "Setting Userge Configs")

        super().__init__(Config.HU_STRING_SESSION,
                         api_id=Config.API_ID,
                         api_hash=Config.API_HASH)

    @staticmethod
    def getLogger(name: str) -> logging.Logger:
        """
        This will return new logger object.
        """

        LOG.debug(LOG_STR, f"Creating Logger => {name}")

        return logging.getLogger(name)

    def getCLogger(self, name: str) -> CLogger:
        """
        This will return new channel logger object.
        """

        LOG.debug(LOG_STR, f"Creating CLogger => {name}")

        return CLogger(self, name)

    @staticmethod
    def new_thread(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """
        Run funcion in new thread.
        """

        async def thread(*args: Any) -> Any:
            loop = asyncio.get_event_loop()

            LOG.debug(LOG_STR, "Creating new thread")

            with ThreadPoolExecutor() as pool:
                return await loop.run_in_executor(pool, func, *args)

        return thread

    async def get_user_dict(self, user_id: int) -> Dict[str, str]:
        """
        This will return user `Dict` which contains
        `fname`(first name), `lname`(last name), `flname`(full name) and `uname`(username).
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

        return {'id': user_obj.id,
                'fname': fname,
                'lname': lname,
                'flname': full_name,
                'uname': username,
                'mention': mention}

    async def send_message(self,
                           chat_id: Union[int, str],
                           text: str,
                           del_in: int = -1,
                           log: bool = False,
                           parse_mode: Union[str, object] = object,
                           disable_web_page_preview: Optional[bool] = None,
                           disable_notification: Optional[bool] = None,
                           reply_to_message_id: Optional[int] = None,
                           schedule_date: Optional[int] = None,
                           reply_markup: Union[InlineKeyboardMarkup,
                                               ReplyKeyboardMarkup,
                                               ReplyKeyboardRemove,
                                               ForceReply] = None) -> Union[Message, bool]:
        """
        Send text messages.

        Example:
                @userge.send_message(chat_id=12345, text='test')

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).
            text (``str``):
                Text of the message to be sent.
            del_in (``int``):
                Time in Seconds for delete that message.
            log (``bool``, *optional*):
                If ``True``, the message will be forwarded to the log channel.
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
            reply_markup (:obj:`InlineKeyboardMarkup` | :obj:`ReplyKeyboardMarkup` | :obj:`ReplyKeyboardRemove` | :obj:`ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
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
            await self.getCLogger(__name__).fwd_msg(msg)

        del_in = del_in or Config.MSG_DELETE_TIMEOUT

        if del_in > 0:
            await asyncio.sleep(del_in)
            return await msg.delete()

        return Message(self, msg)

    def on_cmd(self,
               command: str,
               about: str,
               group: int = 0,
               name: str = '',
               trigger: str = '.',
               filter_me: bool = True,
               **kwargs: Union[str, bool]) -> Callable[[PYROFUNC], PYROFUNC]:
        """
        Decorator for handling messages.

        Example:
                @userge.on_cmd('test', about='for testing')

        Parameters:
            command (``str``):
                command name to execute (without trigger!).
            about (``str``):
                help string for command.
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
                    If ``True``, flags returns without prefix,  defaults to False.
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
            pattern += r"(?:\s([\S\s]+))?$"

        kwargs.update({'cname': cname, 'chelp': about})

        filters_ = Filters.regex(pattern=pattern)

        filter_my_trigger = Filters.create(lambda _, query: \
            query.text.startswith(trigger) if trigger else True)

        sudo_filter = Filters.create(lambda _, query: \
            query.from_user.id in Config.SUDO_USERS and \
                query.text.startswith(Config.SUDO_TRIGGER) if trigger else True)

        sudo_cmd_filter = Filters.create(lambda _, __: \
            cname.lstrip(trigger) in Config.ALLOWED_COMMANDS)

        if filter_me:
            filters_ = filters_ & (
                (Filters.me & filter_my_trigger) | (sudo_filter & sudo_cmd_filter))

        return self.__build_decorator(log=f"On {pattern}",
                                      filters=filters_,
                                      group=group,
                                      **kwargs)

    def on_filters(self,
                   filters: Filters,
                   group: int = 0) -> Callable[[PYROFUNC], PYROFUNC]:
        """
        Decorator for handling filters.
        """

        return self.__build_decorator(log=f"On Filters {filters}",
                                      filters=filters,
                                      group=group)

    def on_new_member(self,
                      welcome_chats: Filters.chat,
                      group: int = -2) -> Callable[[PYROFUNC], PYROFUNC]:
        """
        Decorator for handling new members.
        """

        return self.__build_decorator(log=f"On New Member in {welcome_chats}",
                                      filters=Filters.new_chat_members & welcome_chats,
                                      group=group)

    def on_left_member(self,
                       leaving_chats: Filters.chat,
                       group: int = -2) -> Callable[[PYROFUNC], PYROFUNC]:
        """
        Decorator for handling left members.
        """

        return self.__build_decorator(log=f"On Left Member in {leaving_chats}",
                                      filters=Filters.left_chat_member & leaving_chats,
                                      group=group)

    def get_help(self,
                 key: str = '',
                 all_cmds: bool = False) -> Tuple[Union[str, List[str]], Union[bool, str]]:
        """
        This will return help string for specific key
        or all modules or commands as `List`.
        """

        if not key and not all_cmds:
            return sorted(list(self.__help_dict)), True         # names of all modules

        if not key.startswith('.') and key in self.__help_dict and \
            (len(self.__help_dict[key]) > 1 or list(self.__help_dict[key])[0] != key):
            return sorted(list(self.__help_dict[key])), False   # all commands for that module

        dict_ = {x: y for _, i in self.__help_dict.items() for x, y in i.items()}

        if all_cmds:
            return sorted(list(dict_)), False                   # all commands for .s

        key = key.lstrip('.')
        key_ = '.' + key

        if key in dict_:
            return dict_[key], key      # help text and command for given command

        if key_ in dict_:
            return dict_[key_], key_    # help text and command for modified command

        return '', False                # if unknown

    def __add_help(self,
                   module: str,
                   cname: str = '',
                   chelp: str = '',
                   **_: Union[str, bool]) -> None:
        if cname:
            LOG.debug(LOG_STR, f"Updating Help Dict => [ {cname} : {chelp} ]")

            mname = module.split('.')[-1]

            if mname in self.__help_dict:
                self.__help_dict[mname].update({cname: chelp})

            else:
                self.__help_dict.update({mname: {cname: chelp}})

    def __build_decorator(self,
                          log: str,
                          filters: Filters,
                          group: int,
                          **kwargs: Union[str, bool]) -> Callable[[PYROFUNC], PYROFUNC]:

        def __decorator(func: PYROFUNC) -> PYROFUNC:

            async def __template(_: RawClient, __: RawMessage) -> None:

                await func(Message(_, __, **kwargs))

            LOG.debug(LOG_STR, f"Loading => [ async def {func.__name__}(message) ] " + \
                f"from {func.__module__} `{log}`")

            self.__add_help(func.__module__, **kwargs)

            self.add_handler(MessageHandler(__template, filters), group)

            return func

        return __decorator

    def load_plugin(self, name: str) -> None:
        """
        Load plugin to Userge.
        """

        LOG.debug(LOG_STR, f"Importing {name}")

        self.__imported.append(
            importlib.import_module(f"userge.plugins.{name}"))

        LOG.debug(LOG_STR, f"Imported {self.__imported[-1].__name__} Plugin Successfully")

    def load_plugins(self) -> None:
        """
        Load all Plugins.
        """

        self.__imported.clear()

        LOG.info(LOG_STR, "Importing All Plugins")

        for name in get_all_plugins():
            try:
                self.load_plugin(name)

            except ImportError as i_e:
                LOG.error(LOG_STR, i_e)

        LOG.info(LOG_STR, f"Imported ({len(self.__imported)}) Plugins => " + \
            str([i.__name__ for i in self.__imported]))

    async def reload_plugins(self) -> int:
        """
        Reload all Plugins.
        """

        self.__help_dict.clear()
        reloaded: List[str] = []

        LOG.info(LOG_STR, "Reloading All Plugins")

        for imported in self.__imported:
            try:
                reloaded_ = importlib.reload(imported)

            except ImportError as i_e:
                LOG.error(LOG_STR, i_e)

            else:
                reloaded.append(reloaded_.__name__)

        LOG.info(LOG_STR, f"Reloaded {len(reloaded)} Plugins => {reloaded}")

        return len(reloaded)

    async def restart(self) -> None:
        """
        Restart the Userge.
        """

        LOG.info(LOG_STR, "Restarting Userge")

        await self.stop()

        try:
            c_p = psutil.Process(os.getpid())
            for handler in c_p.open_files() + c_p.connections():
                os.close(handler.fd)

        except Exception as c_e:
            LOG.error(LOG_STR, c_e)

        os.execl(sys.executable, sys.executable, '-m', 'userge')

    def begin(self) -> None:
        """
        This will start the Userge.
        """

        LOG.info(LOG_STR, "Starting Userge")

        nest_asyncio.apply()
        self.run()

        LOG.info(LOG_STR, "Exiting Userge")
