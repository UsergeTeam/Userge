from Userge import log
from os.path import dirname, basename, isfile
import glob


plugins = sorted(
    [
        basename(f)[:-3] for f in glob.glob(dirname(__file__) + "/*.py")
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]
)


log.info(f"plugins to load: {plugins}")

__all__ = plugins + ["plugins"]