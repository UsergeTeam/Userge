from pyrogram import (
    Client, Filters,
    Message, MessageHandler
)

from typing import (
    Dict, Union, Any,
    Callable
)

from .utils import Config, logging

logging.getLogger("pyrogram").setLevel(logging.WARNING)

PYROFUNC = Callable[[Client, Message], Any]


class Userge(Client):

    __HELP_DICT: Dict[str, str] = {}
    __USERGE_MAIN_STRING = "<<<!  #####  ___{}___  #####  !>>>"
    __USERGE_SUB_STRING = "<<<!  {}  !>>>"

    def __init__(self) -> None:
        self.log = logging.getLogger(__name__)

        self.log.info(
            self.__USERGE_MAIN_STRING.format("Setting Userge Configs")
        )

        super().__init__(
            Config.HU_STRING_SESSION,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            plugins=dict(root="userge/plugins")
        )

    def getLogger(
        self,
        name: str
    ) -> logging.Logger:

        self.log.info(
            self.__USERGE_SUB_STRING.format(f"Creating Logger => {name}")
        )

        return logging.getLogger(name)

    def on_cmd(
        self,
        command: str,
        about: str,
        group: int = 0
    ) -> Callable[[PYROFUNC], PYROFUNC]:

        self.__add_help(command, about)

        return self.__build_decorator(
            log=f"On .{command} Command",
            filters=Filters.regex(pattern=f"^.{command}") & Filters.me,
            group=group
        )

    def on_new_member(
        self,
        welcome_chats: Filters.chat,
        group: int = 0
    ) -> Callable[[PYROFUNC], PYROFUNC]:

        return self.__build_decorator(
            log=f"On New Member in {welcome_chats}",
            filters=Filters.new_chat_members & welcome_chats,
            group=group
        )

    def on_left_member(
        self,
        leaving_chats: Filters.chat,
        group: int = 0
    ) -> Callable[[PYROFUNC], PYROFUNC]:

        return self.__build_decorator(
            log=f"On Left Member in {leaving_chats}",
            filters=Filters.left_chat_member & leaving_chats,
            group=group
        )

    def get_help(
        self,
        key: str = ''
    ) -> Union[str, Dict[str, str]]:

        if key and key in self.__HELP_DICT:
            return self.__HELP_DICT[key]

        elif key:
            return ''

        else:
            return self.__HELP_DICT

    def __add_help(
        self,
        command: str,
        about: str
    ) -> None:

        self.log.info(
            self.__USERGE_SUB_STRING.format(f"Updating Help Dict => [ {command} : {about} ]")
        )

        self.__HELP_DICT.update({command: about})

    def __build_decorator(
        self,
        log: str,
        filters: Filters,
        group: int
    ) -> Callable[[PYROFUNC], PYROFUNC]:

        def decorator(func: PYROFUNC) -> PYROFUNC:

            self.log.info(
                self.__USERGE_SUB_STRING.format(f"Loading => [ async def {func.__name__}(client, message) ] `{log}`")
            )

            self.add_handler(MessageHandler(func, filters), group)

            return func

        return decorator

    def begin(self) -> None:

        self.log.info(
            self.__USERGE_MAIN_STRING.format("Starting Userge")
        )

        self.run()

        self.log.info(
            self.__USERGE_MAIN_STRING.format("Exiting Userge")
        )
