# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from os.path import dirname
from userge.utils import get_import_path, logging

LOG = logging.getLogger(__name__)
ROOT = dirname(__file__)


def get_all_plugins():
    plugins = get_import_path(ROOT, "/**/")

    LOG.info(f"all plugins: {plugins}")

    return plugins

__all__ = get_all_plugins()
