from asyncio import sleep
from datetime import datetime
from math import floor
from pathlib import Path
from os import remove
from os.path import join, splitext, basename, dirname, relpath, exists
from zipfile import ZipFile
from threading import Thread
from multiprocessing import Pool, Lock
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified
from userge import userge, Message, Config
from userge.utils import CANCEL_LIST, humanbytes

LOGGER = userge.getLogger(__name__)


class ProcessCanceled(Exception):
    """
    Custom Exception to terminate zipping / unzipping thread.
    """


class Zip:
    """
    Class for ZIP / UNZIP (files / folders).
    """

    __COUNTER_LOCK = Lock()

    def __init__(self, file_path: str) -> None:
        self.__file_path = file_path
        self.__final_file_path = ""
        self.__current = 0
        self.__total = 0
        self.__output = ""
        self.__is_canceled = False
        self.__is_finished = False

    @property
    def completed_files(self) -> int:
        """
        Returns completed files.
        """
        return self.__current

    @property
    def total_files(self) -> int:
        """
        Returns total files.
        """
        return self.__total

    @property
    def percentage(self) -> int:
        """
        Returns percentage.
        """
        return round((self.__current / self.__total) * 100, 2)

    @property
    def progress(self) -> str:
        """
        Returns progress.
        """
        percentage = self.percentage
        progress_str = "[{}{}]".format(
            ''.join(["█" for i in range(floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - floor(percentage / 5))]))

        return progress_str

    @property
    def canceled(self) -> bool:
        """
        Returns True if canceled.
        """
        return self.__is_canceled

    @property
    def finished(self) -> bool:
        """
        Returns True if finished.
        """
        return self.__current == self.__total or self.__is_finished

    def cancel(self) -> None:
        """
        Cancel running thread.
        """
        self.__is_canceled = True

    def __finish(self) -> None:
        self.__is_finished = True

    @property
    def output(self) -> str:
        """
        Returns output.
        """
        return self.__output

    @property
    def final_file_path(self) -> str:
        """
        Returns final file path.
        """
        return self.__final_file_path

    def __zip(self, file_paths: list, final_file_path: str) -> None:
        root = dirname(self.__file_path)

        if exists(final_file_path):
            remove(final_file_path)

        with ZipFile(final_file_path, 'w') as z_f:
            try:
                for file_ in file_paths:

                    if self.__is_canceled:
                        raise ProcessCanceled

                    z_f.write(file_, relpath(file_, root))

                    self.__current += 1

            except ProcessCanceled:
                self.__output = "`process canceled!`"

            except Exception as z_e:
                self.__output = z_e

            finally:
                self.__finish()

    def __counter(self, out_tpl: tuple) -> None:
        c_out, error = out_tpl

        if error:
            self.__output = error
            self.__finish()
            raise Exception(error)

        with self.__COUNTER_LOCK:
            self.__current += c_out

        if self.__is_canceled:
            self.__output = "`process canceled!`"
            self.__finish()
            raise ProcessCanceled

    @staticmethod
    def _unzip(file_path: str, file_names: list, final_file_path: str) -> tuple:
        error = ""

        with ZipFile(file_path, 'r') as z_f:
            for file_name in file_names:
                try:
                    z_f.extract(file_name, final_file_path)

                except FileExistsError:
                    pass

                except Exception as z_e:
                    error = z_e
                    break

        return len(file_names), error

    def zip_path(self) -> None:
        """
        ZIP file path.
        """

        file_paths = []

        def explorer(path: Path) -> None:
            if path.is_file():
                self.__total += 1
                file_paths.append(str(path))

            elif path.is_dir():
                for i in path.iterdir():
                    explorer(i)

        explorer(Path(self.__file_path))

        file_name = basename(self.__file_path) + '.zip'
        self.__final_file_path = join(Config.DOWN_PATH, file_name)

        Thread(target=self.__zip, args=(file_paths, self.__final_file_path)).start()

    def unzip_path(self) -> None:
        """
        UNZIP file path.
        """

        with ZipFile(self.__file_path, 'r') as z_f:
            chunked_file_names = []
            temp_file_names = []
            temp_size = 0
            min_chunk_size = 1024 * 1024 * 10

            for z_obj in z_f.infolist():
                self.__total += 1
                temp_size += z_obj.file_size
                temp_file_names.append(z_obj.filename)

                if temp_size >= min_chunk_size:
                    temp_size = 0
                    chunked_file_names.append(temp_file_names)
                    temp_file_names = []

            if temp_file_names:
                chunked_file_names.append(temp_file_names)

            del temp_file_names, temp_size, min_chunk_size

        dir_name = splitext(basename(self.__file_path))[0]
        self.__final_file_path = join(Config.DOWN_PATH, dir_name)

        pool = Pool()

        for f_n_s in chunked_file_names:
            pool.apply_async(self._unzip,
                             args=(self.__file_path, f_n_s, self.__final_file_path),
                             callback=self.__counter)

        pool.close()

    def get_info(self) -> list:
        """
        Returns ZIP info.
        """

        with ZipFile(self.__file_path, 'r') as z_f:
            return z_f.infolist()


@userge.on_cmd('zip', about="""\
__Zip file / folder__

**Usage:**

    `.zip [file path]`""")
async def zip_(message: Message):
    """zip"""

    file_path = message.input_str

    if not file_path:
        await message.err("missing file path!")

    if not exists(file_path):
        await message.err("file path not exists!")

    start_t = datetime.now()
    z_obj = Zip(file_path)
    z_obj.zip_path()

    tmp = \
        "__Zipping file path...__\n" + \
        "```{}({}%)```\n" + \
        "**File Path** : `{}`\n" + \
        "**Dest** : `{}`\n" + \
        "**Completed** : `{}/{}`"

    while not z_obj.finished:
        if message.message_id in CANCEL_LIST:
            z_obj.cancel()
            CANCEL_LIST.remove(message.message_id)

        try:
            await message.edit(tmp.format(z_obj.progress,
                                          z_obj.percentage,
                                          file_path,
                                          z_obj.final_file_path,
                                          z_obj.completed_files,
                                          z_obj.total_files))
        except MessageNotModified:
            pass

        await sleep(3)

    if z_obj.output:
        await message.err(z_obj.output)

    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(
            f"**zipped** `{file_path}` into `{z_obj.final_file_path}` in {m_s} seconds.")


@userge.on_cmd('unzip', about="""\
__UnZip zip file__

**Usage:**

    `.unzip [zip file path]`""")
async def unzip_(message: Message):
    """unzip"""

    file_path = message.input_str

    if not file_path:
        await message.err("missing file path!")

    if not exists(file_path):
        await message.err("file path not exists!")

    if not file_path.endswith(".zip"):
        await message.err("unsupported file type!")

    start_t = datetime.now()
    z_obj = Zip(file_path)
    z_obj.unzip_path()

    tmp = \
        "__UnZipping file path...__\n" + \
        "```{}({}%)```\n" + \
        "**File Path** : `{}`\n" + \
        "**Dest** : `{}`\n" + \
        "**Completed** : `{}/{}`"

    while not z_obj.finished:
        if message.message_id in CANCEL_LIST:
            z_obj.cancel()
            CANCEL_LIST.remove(message.message_id)

        try:
            await message.edit(tmp.format(z_obj.progress,
                                          z_obj.percentage,
                                          file_path,
                                          z_obj.final_file_path,
                                          z_obj.completed_files,
                                          z_obj.total_files))
        except MessageNotModified:
            pass

        await sleep(3)

    if z_obj.output:
        await message.err(z_obj.output)

    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(
            f"**unzipped** `{file_path}` into `{z_obj.final_file_path}` in {m_s} seconds.")


@userge.on_cmd('zipinfo', about="""\
__File content of Zip file__

**Usage:**

    `.zipinfo [zip file]`""")
async def zipinfo_(message: Message):
    """zipinfo"""

    file_path = message.input_str

    if not file_path:
        await message.err("missing file path!")

    if not exists(file_path):
        await message.err("file path not exists!")

    if not file_path.endswith(".zip"):
        await message.err("unsupported file type!")

    z_obj = Zip(file_path)
    infos = z_obj.get_info()

    output = f"**File Path** : `{file_path}`\n**Total Files** : `{len(infos)}`\n\n"

    for file_ in infos:
        output += f"📄 {file_.filename} __({humanbytes(file_.file_size)})__\n"

    if len(output) >= Config.MAX_MESSAGE_LENGTH:
        await message.send_as_file(text=output, caption=file_path)

    else:
        await message.edit(output)
