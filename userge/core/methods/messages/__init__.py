# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Messages']

from .send_message import SendMessage
from .edit_message_text import EditMessageText
from .send_as_file import SendAsFile


class Messages(SendMessage, EditMessageText, SendAsFile):
    """ methods.messages """
