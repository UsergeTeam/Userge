from Userge import logging

log = logging.getLogger(__name__)


async def get_all_plugins():
    from os.path import dirname, basename, isfile
    import glob

    plugins = sorted(
        [
            basename(f)[:-3] for f in glob.glob(dirname(__file__) + "/*.py")
            if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
        ]
    )

    log.info(f"all plugins: {plugins}")

    return plugins