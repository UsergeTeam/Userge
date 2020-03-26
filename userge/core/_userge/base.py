from typing import Dict
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

    def _msg_to_dict(self,
                     message: Message) -> Dict[str, object]:

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
