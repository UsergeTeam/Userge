<p align="center">
    <a href="https://github.com/UsergeTeam/Userge">
        <img src="resources/userge.png" alt="Userge">
    </a>
    <br>
    <b>Pluggable Telegram UserBot</b>
    <br>
    <a href="https://github.com/UsergeTeam/Userge#inspiration-">Inspiration</a>
    &nbsp•&nbsp
    <a href="https://github.com/UsergeTeam/Userge#features-">Features</a>
    &nbsp•&nbsp
    <a href="https://github.com/UsergeTeam/Userge#example-plugin-">Example</a>
    &nbsp•&nbsp
    <a href="https://github.com/UsergeTeam/Userge#requirements-">Requirements</a>
    &nbsp•&nbsp
    <a href="https://github.com/UsergeTeam/Userge#project-credits-">Project Credits</a>
    &nbsp•&nbsp
    <a href="https://github.com/UsergeTeam/Userge#copyright--license-">Copyright & License</a>
</p>

# Userge 🔥

[![Build Status](https://travis-ci.com/UsergeTeam/Userge.svg?branch=alpha)](https://travis-ci.com/UsergeTeam/Userge)
![Python Version](https://img.shields.io/badge/python-3.8-lightgrey)
![Release](https://img.shields.io/github/v/release/UsergeTeam/Userge)
![Stars](https://img.shields.io/github/stars/UsergeTeam/Userge)
![Forks](https://img.shields.io/github/forks/UsergeTeam/Userge)
![Issues Open](https://img.shields.io/github/issues/UsergeTeam/Userge)
![Issues Closed](https://img.shields.io/github/issues-closed/UsergeTeam/Userge)
![PRs Open](https://img.shields.io/github/issues-pr/UsergeTeam/Userge)
![PRs Closed](https://img.shields.io/github/issues-pr-closed/UsergeTeam/Userge)
![Contributors](https://img.shields.io/github/contributors/UsergeTeam/Userge)
![Repo Size](https://img.shields.io/github/repo-size/UsergeTeam/Userge)
![License](https://img.shields.io/github/license/UsergeTeam/Userge)
![Commit Activity](https://img.shields.io/github/commit-activity/m/UsergeTeam/Userge)
[![Plugins Repo!](https://img.shields.io/badge/Plugins%20Repo-!-orange)](https://github.com/UsergeTeam/Userge-Plugins)
[![Join Channel!](https://img.shields.io/badge/Join%20Channel-!-red)](https://t.me/theUserge)
[![DeepSource](https://static.deepsource.io/deepsource-badge-light-mini.svg)](https://deepsource.io/gh/UsergeTeam/Userge/?ref=repository-badge)
[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/UsergeTeam/Userge)

> **Userge** is a Powerful , _Pluggable_ Telegram UserBot written in _Python_ using [Pyrogram](https://github.com/pyrogram/pyrogram).

## Inspiration 😇

> This project is inspired by the following projects :)

* [tg_userbot](https://github.com/watzon/tg_userbot) ( heavily ) 🤗
* [PyroGramUserBot](https://github.com/SpEcHiDe/PyroGramUserBot)
* [Telegram-Paperplane](https://github.com/RaphielGang/Telegram-Paperplane)
* [UniBorg](https://github.com/SpEcHiDe/UniBorg)

> Special Thanks to all of you !!!.

## Features 😍

* Powerful and Very Useful **built-in** Plugins
  * gdrive [ upload / download / etc ] ( Team Drives Supported! ) 🤥
  * zip / tar / unzip / untar / unrar
  * telegram upload / download
  * pmpermit / afk
  * notes / filters
  * split / combine
  * gadmin
  * plugin manager
  * ...and more
* Channel & Group log support
* Database support
* Build-in help support
* Easy to Setup & Use
* Easy to add / port Plugins
* Easy to write modules with the modified client

## Example Plugin 🤨

```python
from userge import userge, Message, filters

LOG = userge.getLogger(__name__)  # logger object
CHANNEL = userge.getCLogger(__name__)  # channel logger object

# add command handler
@userge.on_cmd("test", about="help text to this command")
async def test_cmd(message: Message):
   LOG.info("starting test command...")  # log to console
   # some other stuff
   await message.edit("testing...", del_in=5)  # this will be automatically deleted after 5 sec
   # some other stuff
   await CHANNEL.log("testing completed!")  # log to channel

# add filters handler
@userge.on_filters(filters.me & filters.private)  # filter my private messages
async def test_filter(message: Message):
   LOG.info("starting filter command...")
   # some other stuff
   await message.reply(f"you typed - {message.text}", del_in=5)
   # some other stuff
   await CHANNEL.log("filter executed!")
```

## Requirements 🥴

* Python 3.8 or Higher 👻
* Telegram [API Keys](https://my.telegram.org/apps)
* Google Drive [API Keys](https://console.developers.google.com/)
* MongoDB [Database URL](https://cloud.mongodb.com/)

## UserGe MODES 🕹

* **USER** mode `(using user account)`
* **BOT** mode `(using bot account)`
* **DUAL** mode `(using both user and bot account)`

  > further **read** [config.env.sample](https://github.com/UsergeTeam/Userge/blob/alpha/config.env.sample)

## How To Deploy 👷

* With Heroku:
    - [**Check Detailed Guide**](https://theuserge.github.io/deployment#deploying-with-heroku)

* With Docker 🐳 
    - [**See Detailed Guide**](https://theuserge.github.io/deployment#deploying-with-docker-)

* With Git, Python and pip 🔧
    -  [**Here's the Detailed Guide**](https://theuserge.github.io/deployment#deploying-with-legacy-method)
  


### Video Tutorial 🎥

  [![Tutorial](resources/tutorial.jpg)](https://youtu.be/M4T_BJvFqkc "Tutorial")

### Support & Discussions 👥

> Head over to the [Discussion Group](https://t.me/usergeot) and [Update Channel](https://t.me/theUserge)

### Project Credits 💆‍♂️

* [Specially to these projects](https://github.com/UsergeTeam/Userge#inspiration-) 🥰
* [@uaudIth](https://t.me/uaudIth)
* [@K_E_N_W_A_Y](https://t.me/K_E_N_W_A_Y)
* [@nawwasl](https://t.me/nawwasl)
* [@TharukaN97](https://t.me/TharukaN97)
* [@Supun97](https://t.me/Supun97)
* [@gotstc](https://t.me/gotstc)

### Copyright & License 👮

* Copyright (C) 2020 by [UsergeTeam](https://github.com/UsergeTeam) ❤️️
* Licensed under the terms of the [GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007](https://github.com/UsergeTeam/Userge/blob/master/LICENSE)
