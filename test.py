# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import asyncio
from userge import userge

async def worker():
    chat_id = int(os.environ.get("CHAT_ID"))
    await userge.send_message(chat_id, 'testing_userge')
    print('sleeping 3 sec...!')
    await asyncio.sleep(3)

async def main():
    print('starting client...!')
    await userge.start()
    tasks = []
    print('adding tasks...!')
    for task in userge._tasks:
        tasks.append(loop.create_task(task()))
    print('stating worker...!')
    await worker()
    print('closing tasks...!')
    for task in tasks:
        task.cancel()
    print('stopping client...!')
    await userge.stop()

loop = asyncio.get_event_loop()
print('creating loop...!')
loop.run_until_complete(main())
print('closing loop...!')
loop.close()

print('userge test has been finished!')
