# Loader

This project helps to manage unlimited plugins repos with one [core repo](https://github.com/UsergeTeam/Userge).

## Main Features

* optimized plugins structure
* unlimited public and private plugins repos support
* custom core repo support
* priority handling
* version controlling
* branch switching
* better control via config file
* only installs required requirements
* plugins conflict handling
* auto requirements conflict resolver
* constraints support (include/exclude/in)
* recovery menu to reset crashed state
* both windows and linux support
* optimized boot time

## Plugins Repo Template

you can fork and edit or refer our [official plugins repo](https://github.com/UsergeTeam/Userge-Plugins)
to get familiar with the new structure.
Also, you can check [custom plugins repo](https://github.com/UsergeTeam/Custom-Plugins) to get a better idea.

## Custom Core Repo

set these env vars

* `CORE_REPO` - repo url (default | https://github.com/UsergeTeam/Userge)
* `CORE_BRANCH` - branch name (default | master)

## [Docker Guide](https://github.com/UsergeTeam/Loader/blob/master/Docker.md)
