from userge.utils import logging


class Base:
    """
    Base Class for Client and Message.
    """

    _MAIN_STRING = "<<<!  #####  ___{}___  #####  !>>>"
    _SUB_STRING = "<<<!  {}  !>>>"
    _LOG = logging.getLogger(__name__)
