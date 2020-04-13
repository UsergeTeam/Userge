<p align="center">
    <a href="https://github.com/UsergeTeam/Userge">
        <img src="resources/userge.png" alt="Userge">
    </a>
    <br>
    <b>Pluggable Telegram UserBot</b>
    <br>
    <a href="https://github.com/UsergeTeam/Userge#inspiration">Inspiration</a>
    &nbsp•&nbsp
    <a href="https://github.com/UsergeTeam/Userge#features">Features</a>
    &nbsp•&nbsp
    <a href="https://github.com/UsergeTeam/Userge#example-plugin">Example</a>
    &nbsp•&nbsp
    <a href="https://github.com/UsergeTeam/Userge#requirements">Requirements</a>
    &nbsp•&nbsp
    <a href="https://github.com/UsergeTeam/Userge#project-credits">Project Credits</a>
    &nbsp•&nbsp
    <a href="https://github.com/UsergeTeam/Userge#copyright--license">Copyright & License</a>
</p>

# Userge

> **Userge** is a Powerful , _Pluggable_ Telegram UserBot written in _Python_ using [Pyrogram](https://github.com/pyrogram/pyrogram).

## Inspiration

> This project is inspired by the following projects :)

* [tg_userbot](https://github.com/watzon/tg_userbot) ( heavily )
* [PyroGramUserBot](https://github.com/SpEcHiDe/PyroGramUserBot)
* [Telegram-Paperplane](https://github.com/RaphielGang/Telegram-Paperplane)
* [UniBorg](https://github.com/SpEcHiDe/UniBorg)

> Special Thanks to all of you !!!.

## Features

* Powerful and Very Useful **built-in** Plugins
  * gdrive ( Team Drives Supported! )
  * zip / unzip
  * telegram upload
  * telegram download
  * etc...
* Channel & Group log support
* Database support
* Build-in help support
* Easy to Setup & Use
* Easy to add / port Plugins
* Easy to write modules with the modified client

## Example Plugin

```python
from userge import userge, Message

LOG = userge.getLogger(__name__)  # logger object

CHANNEL = userge.getCLogger(__name__)  # channel logger object

@userge.on_cmd("test", about="help text to this command")  # adding handler and help text to .test command
async def testing(message: Message):
   LOG.info("starting test command...")  # log to console

   await message.edit("testing...", del_in=5)  # this will be automatically deleted after 5 sec

   CHANNEL.log("testing completed!")  # log to channel
```

## Requirements

* Python 3.6 or Higher
* Telegram [API Keys](https://my.telegram.org/apps)
* Google Drive [API Keys](https://console.developers.google.com/)
* MongoDB [Database URL](https://cloud.mongodb.com/)
  * Step 1

    ![mongo help 1](resources/mongo_help/1.jpg)

  * Step 2

    ![mongo help 2](resources/mongo_help/2.jpg)

  * Step 3

    ![mongo help 3](resources/mongo_help/3.jpg)

  * Step 4

    ![mongo help 4](resources/mongo_help/4.jpg)

  * Step 5

    ![mongo help 5](resources/mongo_help/5.jpg)

  * Step 6

    ![mongo help 6](resources/mongo_help/6.jpg)

  * Step 7

    ![mongo help 7](resources/mongo_help/7.jpg)

  * Final Step

    ![mongo help 8](resources/mongo_help/8.jpg)

    **REMEMBER the password**

## How To Deploy

* [HEROKU](https://www.heroku.com/) Method.

  > First click the button below.  
  > If you don't have HU_STRING_SESSION just ignore it.  
  > After Deployed to Heroku first turn off the app (resources -> turn off) and run `bash genStr` in console (more -> run console).  
  > After that copy the string session and past it in Config Vars (settings -> reveal config vars).  
  > Finally turn on the app and check the logs (settings -> view logs) :)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/dacadcbabdb74de3903ddae25dc95375)](https://app.codacy.com/gh/UsergeTeam/Userge?utm_source=github.com&utm_medium=referral&utm_content=UsergeTeam/Userge&utm_campaign=Badge_Grade_Dashboard)
  [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/UsergeTeam/Userge)

* Other Method.

  ```bash
  # clone the repo
  git clone https://github.com/UsergeTeam/Userge.git
  cd Userge

  # create virtualenv
  virtualenv -p /usr/bin/python3 venv
  . ./venv/bin/activate

  # install requirements
  pip install -r requirements.txt

  # Create config.env as given config.env.sample and fill that
  cp config.env.sample config.env

  # get string session and add it to config.env
  bash genStr

  # finally run the Userge ;)
  bash run
  ```

> TODO: add Docker Support.

### Support & Discussions

> Head over to the [Discussion Group](https://t.me/slbotsbugs) and [Update Channel](https://t.me/theUserge)

### Project Credits

* [Specially to these projects](https://github.com/UsergeTeam/Userge#inspiration)
* [@uaudIth](https://t.me/uaudIth)
* [@K_E_N_W_A_Y](https://t.me/K_E_N_W_A_Y)
* [@nawwasl](https://t.me/nawwasl)
* [@gotstc](https://t.me/gotstc)

### Copyright & License

* Copyright (C) 2020 by [UsergeTeam](https://github.com/UsergeTeam)
* Licensed under the terms of the [GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007](https://github.com/UsergeTeam/Userge/blob/master/LICENSE)
