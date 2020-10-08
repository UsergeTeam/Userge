import os

import time

import asyncio

from re import sub

from collections import deque

from random import choice, getrandbits, randint

import wget

import requests

from cowpy import cow

from userge import userge, Message


@userge.on_cmd("mar$", about={'header': "doob maro"})

async def doobmaro_(message: Message):

    """doobmaro_"""

    await message.edit('`Doob maro 🤦‍♂️,plox😐abb jikar bhi kya karoge`')
