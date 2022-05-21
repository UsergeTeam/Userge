""" create poll, vote poll, stop poll, retract vote """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

# By @Krishna_Singhal

import random

from userge import userge, Message


@userge.on_cmd("poll", about={
    'header': "Create Poll of Suggestion to get opinion",
    'flags': {'-n': "Use to Make poll non-anonymous"},
    'usage': "{tr}poll [reply to ques text]"},
    allow_private=False)
async def create_poll(msg: Message):
    """" Create poll """
    options = ["Yes, Sure 😎", "No interest 🙄", "What..? 😳😳🤔🤔"]
    anonymous = True
    if '-n' in msg.flags:
        anonymous = False
    replied = msg.reply_to_message
    if replied:
        query = "Do you agree with that replied Suggestion..?"
        msg_id = replied.message_id
        await userge.send_poll(
            chat_id=msg.chat.id,
            question=query,
            options=options,
            is_anonymous=anonymous,
            reply_to_message_id=msg_id)
    else:
        query = "Do you agree with that Suggestion..?"
        await userge.send_poll(
            chat_id=msg.chat.id,
            question=query,
            options=options,
            is_anonymous=anonymous)
    await msg.delete()


@userge.on_cmd("vote", about={
    'header': "Vote poll",
    'description': "Options Should be in numeric",
    'usage': "{tr}vote [option | reply to poll]",
    'examples': "{tr}vote 1 (with reply to poll)"},
    allow_private=False)
async def vote_poll(msg: Message):
    """ vote poll """

    replied = msg.reply_to_message
    if replied and replied.poll:
        if msg.input_str and msg.input_str.isnumeric():
            option = int(msg.input_str) - 1
        else:
            option = random.randint(0, len(replied.poll.options) - 1)

        try:
            await userge.vote_poll(msg.chat.id, replied.message_id, option)
        except Exception as e_f:
            await msg.err(e_f)
        else:
            await msg.edit("`Votted poll...`")
    else:
        await msg.err("How can I vote without reply to poll")


@userge.on_cmd("stop", about={
    'header': "Stop a poll which was sent by you.",
    'usage': "{tr}stop [reply to poll]"},
    allow_private=False)
async def stop_poll(msg: Message):
    """ Stop poll """

    replied = msg.reply_to_message

    if replied and replied.poll:
        try:
            await userge.stop_poll(msg.chat.id, replied.message_id)
        except Exception as e_f:
            await msg.err(e_f)
        else:
            await msg.edit("`Poll Stopped...`")
    else:
        await msg.err("How can I stop poll without reply a poll")


@userge.on_cmd("retract", about={
    'header': "Retract your vote in a Poll",
    'usage': "{tr}retract [reply to poll]"},
    allow_private=False)
async def retract_vote(msg: Message):
    """ Retract vote """

    replied = msg.reply_to_message

    if replied and replied.poll:
        try:
            await userge.retract_vote(msg.chat.id, replied.message_id)
        except Exception as e_f:
            await msg.err(e_f)
        else:
            await msg.edit("`Vote retracted...`")
    else:
        await msg.err("How can I retract your vote without reply a poll")
