import re
import nest_asyncio
from userge.utils import Config, logging
from typing import Dict, List, Union, Any, Callable
from .base import Base
from .message import Message
from pyrogram import Client, Filters, MessageHandler

logging.getLogger("pyrogram").setLevel(logging.WARNING)

PYROFUNC = Callable[[Message], Any]


class Userge(Client, Base):
    """
    Userge: userbot
    """
    
    __HELP_DICT: Dict[str, Dict[str, str]] = {}

    def __init__(self) -> None:
        self._LOG.info(
            self._MAIN_STRING.format("Setting Userge Configs"))

        super().__init__(Config.HU_STRING_SESSION,
                         api_id=Config.API_ID,
                         api_hash=Config.API_HASH,
                         plugins=dict(root="userge/plugins"))

    def getLogger(self,
                  name: str) -> logging.Logger:
        """
        This will return new logger object.
        """

        self._LOG.info(
            self._SUB_STRING.format(f"Creating Logger => {name}"))

        return logging.getLogger(name)

    async def get_user_dict(self,
                            user_id: int) -> Dict[str, str]:
        """
        This will return user `Dict` which contains
        `fname`, `lname`, `flname` and `uname`.
        """

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
               only_me: bool = True,
               **kwargs) -> Callable[[PYROFUNC], PYROFUNC]:
        """
        Decorator for handling messages.

        Example:
            .. code-block:: python
                @userge.on_cmd('test', about='for testing')
        Parameters:
            command (``str``):
                command name to execute (without trigger!).
            about (``str``):
                help string for command.
            group (``int``, *optional*):
                The group identifier, defaults to 0.
            trigger (``str``, *optional*):
                trigger to start command, defaults to '.'.
            only_me (``bool``, *optional*):
                If ``True``, Filters.me = True,  defaults to True.
            kwargs:
                prefix (``str``, *optional*):
                    set prefix for flags, defaults to '-'.
                del_pre (``bool``, *optional*):
                    If ``True``, flags returns without prefix,  defaults to False.
        """

        found = [i for i in '()[]+*.\\|?:' if i in command]

        if found:
            match = re.match(r"([\w_]+)", command)
            cname = match.groups()[0] if match else ''
            pattern = f"\\{trigger}{command}"

        else:
            cname = command
            pattern = f"^\\{trigger}{command}(?:\\s([\\S\\s]+))?$"

        kwargs.update({'cname': cname, 'chelp': about})

        filters_ = Filters.regex(pattern=pattern) & Filters.me if only_me \
            else Filters.regex(pattern=pattern)

        return self.__build_decorator(log=f"On {pattern}",
                                      filters=filters_,
                                      group=group,
                                      **kwargs)

    def on_new_member(self,
                      welcome_chats: Filters.chat,
                      group: int = 0) -> Callable[[PYROFUNC], PYROFUNC]:
        """
        Decorator for handling new members.
        """

        return self.__build_decorator(log=f"On New Member in {welcome_chats}",
                                      filters=Filters.new_chat_members & welcome_chats,
                                      group=group)

    def on_left_member(self,
                       leaving_chats: Filters.chat,
                       group: int = 0) -> Callable[[PYROFUNC], PYROFUNC]:
        """
        Decorator for handling left members.
        """

        return self.__build_decorator(log=f"On Left Member in {leaving_chats}",
                                      filters=Filters.left_chat_member & leaving_chats,
                                      group=group)

    def get_help(self,
                 key: str = '') -> Union[str, List[str]]:
        """
        This will return help string for specific key
        or all help strings as `Dict`.
        """

        if not key:
            return list(self.__HELP_DICT), True # module names

        if not key.startswith('.') and key in self.__HELP_DICT:
            return list(self.__HELP_DICT[key]), False # all commands for that module

        dict_ = {x: y for _, i in self.__HELP_DICT.items() for x, y in i.items()}

        if key.lstrip('.') in dict_:
            return dict_[key.lstrip('.')], False # help text for that command

        else:
            return '', False # unknown

    def __add_help(self,
                   module: str,
                   cname: str = '',
                   chelp: str = '',
                   **kwargs) -> None:
        if cname:
            self._LOG.info(
                self._SUB_STRING.format(f"Updating Help Dict => [ {cname} : {chelp} ]"))

            mname = module.split('.')[-1]

            if mname in self.__HELP_DICT:
                self.__HELP_DICT[mname].update({cname: chelp})

            else:
                self.__HELP_DICT.update({mname: {cname: chelp}})

    def __build_decorator(self,
                          log: str,
                          filters: Filters,
                          group: int,
                          **kwargs) -> Callable[[PYROFUNC], PYROFUNC]:

        def __decorator(func: PYROFUNC) -> PYROFUNC:
            async def __template(_: Client,
                                 message: Message) -> None:

                await func(Message(self, message, **kwargs))

            self._LOG.info(
                self._SUB_STRING.format(
                    f"Loading => [ async def {func.__name__}(message) ] from {func.__module__} `{log}`"))

            self.__add_help(func.__module__, **kwargs)

            self.add_handler(MessageHandler(__template, filters), group)

            return func

        return __decorator

    def begin(self) -> None:
        """
        This will start the Userge.
        """

        self._LOG.info(
            self._MAIN_STRING.format("Starting Userge"))

        nest_asyncio.apply()

        self.run()

        self._LOG.info(
            self._MAIN_STRING.format("Exiting Userge"))
