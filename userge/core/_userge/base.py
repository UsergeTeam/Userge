import asyncio
from typing import Dict, Callable
from concurrent.futures import ThreadPoolExecutor
from pyrogram import Message
import nest_asyncio
from userge.utils import logging


class Base:
    """
    Base Class for Client and Message.
    """

    _MAIN_STRING = "<<<!  #####  ___{}___  #####  !>>>"
    _SUB_STRING = "<<<!  {}  !>>>"
    _LOG = logging.getLogger(__name__)
    _NST_ASYNC = nest_asyncio

    def getLogger(self, name: str) -> logging.Logger:
        """
        This will return new logger object.
        """

        self._LOG.info(
            self._SUB_STRING.format(f"Creating Logger => {name}"))

        return logging.getLogger(name)

    def _msg_to_dict(self,
                     message: Message) -> Dict[str, object]:
        """
        Convert message obj to dict.
        """

        kwargs_ = vars(message)
        del message

        del kwargs_['_client']

        if '_Message__filtered_input_str' in kwargs_:
            del kwargs_['_Message__filtered_input_str']

        if '_Message__flags' in kwargs_:
            del kwargs_['_Message__flags']

        if '_Message__kwargs' in kwargs_:
            del kwargs_['_Message__kwargs']

        return kwargs_

    def new_thread(self, func: Callable) -> Callable:
        """
        Run funcion in new thread.
        """

        async def thread(*args, **kwargs):
            loop = asyncio.get_event_loop()

            with ThreadPoolExecutor() as pool:
                return await loop.run_in_executor(pool, func,
                                                  *args, **kwargs)

        return thread
