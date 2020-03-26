from os.path import dirname
from userge.utils import get_import_path, logging

LOG = logging.getLogger(__name__)
ROOT = dirname(__file__)


def get_all_plugins():
    plugins = get_import_path(ROOT, "/**/")

    LOG.info(f"all plugins: {plugins}")

    return plugins

__all__ = get_all_plugins()
