import re
import nest_asyncio
from userge.utils import Config, logging
from typing import Dict, Union, Any, Callable
from .base import Base
from .message import Message
from pyrogram import Client, Filters, MessageHandler

logging.getLogger("pyrogram").setLevel(logging.WARNING)

PYROFUNC = Callable[[Message], Any]


class Userge(Base, Client):
    __HELP_DICT: Dict[str, str] = {}

    def __init__(self) -> None:
        self._LOG.info(
            self._MAIN_STRING.format("Setting Userge Configs"))

        super().__init__(Config.HU_STRING_SESSION,
                         api_id=Config.API_ID,
                         api_hash=Config.API_HASH,
                         plugins=dict(root="userge/plugins"))

    def getLogger(self,
                  name: str) -> logging.Logger:

        self._LOG.info(
            self._SUB_STRING.format(f"Creating Logger => {name}"))

        return logging.getLogger(name)

    async def get_user_dict(self,
                            user_id: int) -> Dict[str, str]:

        user_obj = await self.get_users(user_id)

        fname = user_obj.first_name or ''
        lname = user_obj.last_name or ''
        username = user_obj.username or ''

        if fname and lname:
            full_name = fname + ' ' + lname

        elif fname or lname:
            full_name = fname or lname

        else:
            full_name = "user"

        return {'fname': fname,
                'lname': lname,
                'flname': full_name,
                'uname': username}

    def on_cmd(self,
               command: str,
               about: str,
               group: int = 0,
               trigger: str = '.',
               only_me: bool = True
               ) -> Callable[[PYROFUNC], PYROFUNC]:

        found = [i for i in '()[]+*.\\|?:' if i in command]

        if found:
            match = re.match(r"([\w_]+)", command)
            command_name = match.groups()[0] if match else ''
            pattern = f"{trigger}{command}"

        else:
            command_name = command
            pattern = f"^{trigger}{command}(?:\\s([\\S\\s]+))?$"

        if command_name:
            self.__add_help(command_name, about)

        filters_ = Filters.regex(pattern=pattern) & Filters.me if only_me \
            else Filters.regex(pattern=pattern)

        return self.__build_decorator(log=f"On .{command_name} Command",
                                      filters=filters_,
                                      group=group
                                      )

    def on_new_member(self,
                      welcome_chats: Filters.chat,
                      group: int = 0) -> Callable[[PYROFUNC], PYROFUNC]:

        return self.__build_decorator(log=f"On New Member in {welcome_chats}",
                                      filters=Filters.new_chat_members & welcome_chats,
                                      group=group)

    def on_left_member(self,
                       leaving_chats: Filters.chat,
                       group: int = 0) -> Callable[[PYROFUNC], PYROFUNC]:

        return self.__build_decorator(log=f"On Left Member in {leaving_chats}",
                                      filters=Filters.left_chat_member & leaving_chats,
                                      group=group)

    def get_help(self,
                 key: str = '') -> Union[str, Dict[str, str]]:

        if key and key in self.__HELP_DICT:
            return self.__HELP_DICT[key]

        elif key:
            return ''

        else:
            return self.__HELP_DICT

    def __add_help(self,
                   command: str,
                   about: str) -> None:

        self._LOG.info(
            self._SUB_STRING.format(f"Updating Help Dict => [ {command} : {about} ]"))

        self.__HELP_DICT.update({command: about})

    def __build_decorator(self,
                          log: str,
                          filters: Filters,
                          group: int
                          ) -> Callable[[PYROFUNC], PYROFUNC]:

        def __decorator(func: PYROFUNC) -> PYROFUNC:
            async def __template(_: Client,
                                 message: Message) -> None:

                await func(Message(message, self, **kwargs))

            self._LOG.info(
                self._SUB_STRING.format(
                    f"Loading => [ async def {func.__name__}(message) ] `{log}`"))

            self.add_handler(MessageHandler(__template, filters), group)

            return func

        return __decorator

    def begin(self) -> None:

        self._LOG.info(
            self._MAIN_STRING.format("Starting Userge"))

        nest_asyncio.apply()

        self.run()

        self._LOG.info(
            self._MAIN_STRING.format("Exiting Userge"))
