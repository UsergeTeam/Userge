# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import os
from time import time
from glob import glob
from asyncio import sleep
from datetime import datetime
from math import floor, ceil
from pathlib import Path
from shutil import rmtree
from os.path import (
    join, splitext, basename, dirname, relpath, exists, isdir, isfile)
from zipfile import ZipFile, is_zipfile
from tarfile import TarFile, is_tarfile, open as tar_open
from threading import Thread
from multiprocessing import Pool, Lock
from typing import Union, List, Tuple, Sequence

from userge import userge, Message, Config
from userge.utils import humanbytes, time_formatter
from userge.utils.exceptions import ProcessCanceled

LOGGER = userge.getLogger(__name__)
COUNTER_LOCK = Lock()


class BaseLib:
    """
    Base Class for PackLib and SCLib.
    """

    def __init__(self) -> None:
        self._final_file_path = ""
        self._current = 0
        self._total = 0
        self._output = ""
        self._is_canceled = False
        self._is_finished = False

    @property
    def completed_files(self) -> int:
        """
        Returns completed files.
        """
        return self._current

    @property
    def total_files(self) -> int:
        """
        Returns total files.
        """
        return self._total

    @property
    def percentage(self) -> int:
        """
        Returns percentage.
        """
        return int(round((self._current / self._total) * 100, 2))

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
        return self._is_canceled

    @property
    def finished(self) -> bool:
        """
        Returns True if finished.
        """
        return self._current == self._total or self._is_finished

    def cancel(self) -> None:
        """
        Cancel running thread.
        """
        self._is_canceled = True

    def _finish(self) -> None:
        self._is_finished = True

    @property
    def output(self) -> str:
        """
        Returns output.
        """
        return self._output

    @property
    def final_file_path(self) -> str:
        """
        Returns final file path.
        """
        return self._final_file_path


class PackLib(BaseLib):
    """
    Class for PACK / UNPACK / LISTPACK (files / folders).
    """

    def __init__(self, file_path: str) -> None:
        self.__file_path = file_path
        super().__init__()

    def __zip(self,
              p_type: Union[ZipFile, TarFile],
              file_paths: List[str],
              final_file_path: str) -> None:

        root = dirname(self.__file_path)

        if exists(final_file_path):
            os.remove(final_file_path)

        with p_type(final_file_path, 'w') as p_f:
            try:
                for file_ in file_paths:

                    if self._is_canceled:
                        raise ProcessCanceled

                    if isinstance(p_f, ZipFile):
                        p_f.write(file_, relpath(file_, root))

                    else:
                        p_f.add(file_, relpath(file_, root))

                    self._current += 1

            except ProcessCanceled:
                self._output = "`process canceled!`"

            except Exception as z_e:
                LOGGER.exception(z_e)
                self._output = str(z_e)

            finally:
                self._finish()

    def __counter(self, out_tpl: Tuple[int, str]) -> None:
        c_out, error = out_tpl

        if error:
            self._output = error
            self._finish()
            raise Exception(error)

        with COUNTER_LOCK:
            self._current += c_out

        if self._is_canceled:
            self._output = "`process canceled!`"
            self._finish()
            raise ProcessCanceled

    @staticmethod
    def _unpack(file_path: str, file_names: List[str], final_file_path: str) -> Tuple[int, str]:
        error = ""

        if is_zipfile(file_path):
            u_type = ZipFile

        else:
            u_type = tar_open

        with u_type(file_path, 'r') as p_f:
            for file_name in file_names:
                try:
                    p_f.extract(file_name, final_file_path)

                except FileExistsError:
                    pass

                except Exception as z_e:
                    LOGGER.exception(z_e)
                    error = str(z_e)
                    break

        return len(file_names), error

    def pack_path(self, tar: bool) -> None:
        """
        PACK file path.
        """

        file_paths = []

        def explorer(path: Path) -> None:
            if path.is_file():
                self._total += 1
                file_paths.append(str(path))

            elif path.is_dir():
                for i in path.iterdir():
                    explorer(i)

        explorer(Path(self.__file_path))
        file_name = basename(self.__file_path)

        if tar:
            file_name += '.tar'
            p_type = tar_open

        else:
            file_name += '.zip'
            p_type = ZipFile

        self._final_file_path = join(Config.DOWN_PATH, file_name)

        Thread(target=self.__zip, args=(p_type, file_paths, self._final_file_path)).start()

    def unpack_path(self) -> None:
        """
        UNPACK file path.
        """

        chunked_file_names = []
        temp_file_names = []
        temp_size = 0
        min_chunk_size = 1024 * 1024 * 10

        for f_n, f_s in self.get_info():
            self._total += 1
            temp_size += f_s
            temp_file_names.append(f_n)

            if temp_size >= min_chunk_size:
                temp_size = 0
                chunked_file_names.append(temp_file_names)
                temp_file_names = []

        if temp_file_names:
            chunked_file_names.append(temp_file_names)

        del temp_file_names, temp_size, min_chunk_size

        dir_name = splitext(basename(self.__file_path))[0]
        self._final_file_path = join(
            Config.DOWN_PATH, dir_name.replace('.tar', '').replace('.', '_'))

        pool = Pool()

        for f_n_s in chunked_file_names:
            pool.apply_async(self._unpack,
                             args=(self.__file_path, f_n_s, self._final_file_path),
                             callback=self.__counter)

        pool.close()

    def get_info(self) -> Sequence[Tuple[str, int]]:
        """
        Returns PACK info.
        """

        if is_zipfile(self.__file_path):
            with ZipFile(self.__file_path, 'r') as z_f:
                return tuple((z_.filename, z_.file_size) for z_ in z_f.infolist())

        else:
            with tar_open(self.__file_path, 'r') as t_f:
                return tuple((t_.name, t_.size) for t_ in t_f.getmembers())

    @staticmethod
    def is_supported(file_path: str) -> bool:
        """
        Returns file is supported or not.
        """

        return is_zipfile(file_path) or is_tarfile(file_path)


class SCLib(BaseLib):
    """
    Class for split / combine files.
    """

    def __init__(self, file_path: str) -> None:
        self.__chunk_size = 1024 * 1024
        self.__s_time = time()
        self.__path = file_path
        self.__file_size = 0
        self.__cmp_size = 0
        super().__init__()

    @property
    def completed(self) -> int:
        """
        Returns completed file size.
        """
        return self.__cmp_size

    @property
    def total(self) -> int:
        """
        Returns total file size.
        """
        return self.__file_size

    @property
    def percentage(self) -> int:
        """
        Returns percentage.
        """
        return int(round((self.__cmp_size / self.__file_size) * 100, 2))

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
    def speed(self) -> float:
        """
        Returns speed.
        """
        return int(round(self.__cmp_size / (time() - self.__s_time), 2))

    @property
    def eta(self) -> str:
        """
        Returns eta.
        """
        return time_formatter(
            (self.__file_size - self.__cmp_size) / self.speed if self.speed else 0)

    def __split_worker(self, times: int) -> None:

        try:
            with open(self.__path, "rb") as o_f:
                for self._current in range(self._total):

                    if self._is_canceled:
                        raise ProcessCanceled

                    t_p = join(
                        self._final_file_path,
                        f"{basename(self.__path)}.{str(self._current).zfill(5)}")

                    with open(t_p, "wb") as s_f:
                        for _ in range(times):
                            chunk = o_f.read(self.__chunk_size)

                            if self._is_canceled:
                                raise ProcessCanceled

                            if not chunk:
                                break

                            s_f.write(chunk)
                            self.__cmp_size += len(chunk)

        except ProcessCanceled:
            self._output = "`process canceled!`"

        except Exception as s_e:
            LOGGER.exception(s_e)
            self._output = str(s_e)

        finally:
            self._finish()

    def __combine_worker(self, file_list: List[str]) -> None:

        try:
            with open(self._final_file_path, "wb") as o_f:
                for file_path in file_list:

                    if self._is_canceled:
                        raise ProcessCanceled

                    with open(file_path, "rb") as s_f:
                        while True:
                            chunk = s_f.read(self.__chunk_size)

                            if self._is_canceled:
                                raise ProcessCanceled

                            if not chunk:
                                break

                            o_f.write(chunk)
                            self.__cmp_size += len(chunk)

                    self._current += 1

        except ProcessCanceled:
            self._output = "`process canceled!`"

        except Exception as c_e:
            LOGGER.exception(c_e)
            self._output = str(c_e)

        finally:
            self._finish()

    def split(self, split_size: int) -> None:
        """
        Split files.
        """

        split_size = int(split_size) * 1024 * 1024
        self.__file_size = os.stat(self.__path).st_size

        if self.__chunk_size > split_size:
            self.__chunk_size = split_size

        times = int(ceil(split_size / self.__chunk_size))
        self._total = int(ceil(self.__file_size / split_size))

        self._final_file_path = join(
            dirname(self.__path), f"split_{basename(self.__path).replace('.', '_')}")

        if not isdir(self._final_file_path):
            os.makedirs(self._final_file_path)

        Thread(target=self.__split_worker, args=(times,)).start()

    def combine(self) -> None:
        """
        Combine Split files.
        """

        file_name, ext = splitext(basename(self.__path))
        self._final_file_path = join(dirname(self.__path), file_name)
        file_list = sorted(glob(self._final_file_path + f".{'[0-9]' * len(ext.lstrip('.'))}"))

        self._total = len(file_list)
        self.__file_size = sum([os.stat(f_).st_size for f_ in file_list])

        Thread(target=self.__combine_worker, args=(file_list,)).start()


@userge.on_cmd('setdir', about={
    'header': "set temporary working directory",
    'usage': ".setdir [path / name]"})
async def setdir_(message: Message) -> None:
    """setdir"""

    path = message.input_str
    if not path:
        await message.err("missing file path!")
        return

    try:
        if not isdir(path):
            os.makedirs(path)

        Config.DOWN_PATH = path
        await message.edit(f"set `{path}` as **working directory** successfully!", del_in=5)

    except Exception as p_e:
        await message.err(p_e)


@userge.on_cmd("cleardir", about={'header': "Clear the current working directory"})
async def clear_dir_(message: Message):
    """clear dir"""

    if not isdir(Config.DOWN_PATH):
        await message.edit(
            f'path : `{Config.DOWN_PATH}` not found and just created!', del_in=5)

    else:
        rmtree(Config.DOWN_PATH, True)
        await message.edit(
            f'path : `{Config.DOWN_PATH}` **cleared** successfully!', del_in=5)

    os.makedirs(Config.DOWN_PATH)


@userge.on_cmd('rmdir', about={
    'header': "delete a directory or file",
    'usage': ".rmdir [path / name]"})
async def rmdir_(message: Message) -> None:
    """rmdir"""

    path = message.input_str
    if not path:
        await message.err("missing file path!")
        return

    if not exists(path):
        await message.err("file path not exists!")
        return

    rmtree(path)
    await message.edit(f"path : `{path}` **deleted** successfully!", del_in=5)


@userge.on_cmd(r'split (\d+) ([\s\S]+)', about={
    'header': "Split files",
    'usage': ".split [split size (MB)] [file path]",
    'examples': ".split 5 downloads/test.zip"})
async def split_(message: Message) -> None:
    """split"""

    split_size = int(message.matches[0].group(1))
    file_path = str(message.matches[0].group(2))

    if not file_path:
        await message.err("missing file path!")
        return

    if not isfile(file_path):
        await message.err("file path not exists!")
        return

    await message.edit("`processing...`")

    start_t = datetime.now()
    s_obj = SCLib(file_path)
    s_obj.split(split_size)

    tmp = \
        "__Splitting file path...__\n" + \
        "```{}({}%)```\n" + \
        "**File Path** : `{}`\n" + \
        "**Dest** : `{}`\n" + \
        "**Completed** : `{}`\n" + \
        "**Total** : `{}`\n" + \
        "**Speed** : `{}/s`\n" + \
        "**ETA** : `{}`\n" + \
        "**Completed Files** : `{}/{}`"

    while not s_obj.finished:
        if message.process_is_canceled:
            s_obj.cancel()

        await message.try_to_edit(tmp.format(s_obj.progress,
                                             s_obj.percentage,
                                             file_path,
                                             s_obj.final_file_path,
                                             humanbytes(s_obj.completed),
                                             humanbytes(s_obj.total),
                                             humanbytes(s_obj.speed),
                                             s_obj.eta,
                                             s_obj.completed_files,
                                             s_obj.total_files))

        await sleep(3)

    if s_obj.output:
        await message.err(s_obj.output)

    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(
            f"**split** `{file_path}` into `{s_obj.final_file_path}` "
            f"in `{m_s}` seconds.", log=True)


@userge.on_cmd('combine', about={
    'header': "Combine split files",
    'usage': ".combine [file path]",
    'examples': ".combine downloads/test.tar.00000"})
async def combine_(message: Message) -> None:
    """combine"""

    file_path = message.input_str
    if not file_path:
        await message.err("missing file path!")
        return

    if not isfile(file_path):
        await message.err("file path not exists!")
        return

    _, ext = splitext(basename(file_path))

    if not ext.lstrip('.').isdigit():
        await message.err("unsupported file!")
        return

    await message.edit("`processing...`")

    start_t = datetime.now()
    c_obj = SCLib(file_path)
    c_obj.combine()

    tmp = \
        "__Combining file path...__\n" + \
        "```{}({}%)```\n" + \
        "**File Path** : `{}`\n" + \
        "**Dest** : `{}`\n" + \
        "**Completed** : `{}`\n" + \
        "**Total** : `{}`\n" + \
        "**Speed** : `{}/s`\n" + \
        "**ETA** : `{}`\n" + \
        "**Completed Files** : `{}/{}`"

    while not c_obj.finished:
        if message.process_is_canceled:
            c_obj.cancel()

        await message.try_to_edit(tmp.format(c_obj.progress,
                                             c_obj.percentage,
                                             file_path,
                                             c_obj.final_file_path,
                                             humanbytes(c_obj.completed),
                                             humanbytes(c_obj.total),
                                             humanbytes(c_obj.speed),
                                             c_obj.eta,
                                             c_obj.completed_files,
                                             c_obj.total_files))

        await sleep(3)

    if c_obj.output:
        await message.err(c_obj.output)

    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(
            f"**combined** `{file_path}` into `{c_obj.final_file_path}` "
            f"in `{m_s}` seconds.", log=True)


@userge.on_cmd('zip', about={
    'header': "Zip file / folder",
    'usage': ".zip [file path | folder path]"})
async def zip_(message: Message) -> None:
    """zip"""
    await _pack_helper(message)


@userge.on_cmd('tar', about={
    'header': "Tar file / folder",
    'usage': ".tar [file path | folder path]"})
async def tar_(message: Message) -> None:
    """tar"""
    await _pack_helper(message, True)


async def _pack_helper(message: Message, tar: bool = False) -> None:
    file_path = message.input_str

    if not file_path:
        await message.err("missing file path!")
        return

    if not exists(file_path):
        await message.err("file path not exists!")
        return

    await message.edit("`processing...`")
    start_t = datetime.now()
    p_obj = PackLib(file_path)
    p_obj.pack_path(tar)

    tmp = \
        "__Packing file path...__\n" + \
        "```{}({}%)```\n" + \
        "**File Path** : `{}`\n" + \
        "**Dest** : `{}`\n" + \
        "**Completed** : `{}/{}`"

    while not p_obj.finished:
        if message.process_is_canceled:
            p_obj.cancel()

        await message.try_to_edit(tmp.format(p_obj.progress,
                                             p_obj.percentage,
                                             file_path,
                                             p_obj.final_file_path,
                                             p_obj.completed_files,
                                             p_obj.total_files))

        await sleep(3)

    if p_obj.output:
        await message.err(p_obj.output)

    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(
            f"**packed** `{file_path}` into `{p_obj.final_file_path}` "
            f"in `{m_s}` seconds.", log=True)


@userge.on_cmd('unpack', about={
    'header': "unpack packed file",
    'usage': ".unpack [zip file path | tar file path]"})
async def unpack_(message: Message) -> None:
    """unpack"""

    file_path = message.input_str

    if not file_path:
        await message.err("missing file path!")
        return

    if not exists(file_path):
        await message.err("file path not exists!")
        return

    if not PackLib.is_supported(file_path):
        await message.err("unsupported file type!")
        return

    await message.edit("`processing...`")
    start_t = datetime.now()
    p_obj = PackLib(file_path)
    p_obj.unpack_path()

    tmp = \
        "__UnPacking file path...__\n" + \
        "```{}({}%)```\n" + \
        "**File Path** : `{}`\n" + \
        "**Dest** : `{}`\n" + \
        "**Completed** : `{}/{}`"

    while not p_obj.finished:
        if message.process_is_canceled:
            p_obj.cancel()

        await message.try_to_edit(tmp.format(p_obj.progress,
                                             p_obj.percentage,
                                             file_path,
                                             p_obj.final_file_path,
                                             p_obj.completed_files,
                                             p_obj.total_files))

        await sleep(3)

    if p_obj.output:
        await message.err(p_obj.output)

    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(
            f"**unpacked** `{file_path}` into `{p_obj.final_file_path}` "
            f"in `{m_s}` seconds.", log=True)


@userge.on_cmd('packinfo', about={
    'header': "File content of the pack",
    'usage': ".packinfo [zip file path | tar file path]"})
async def packinfo_(message: Message) -> None:
    """packinfo"""

    file_path = message.input_str

    if not file_path:
        await message.err("missing file path!")
        return

    if not exists(file_path):
        await message.err("file path not exists!")
        return

    if not PackLib.is_supported(file_path):
        await message.err("unsupported file type!")
        return

    await message.edit("`processing...`")
    p_obj = PackLib(file_path)
    infos = p_obj.get_info()

    output = f"**File Path** : `{file_path}`\n**Total Files** : `{len(infos)}`\n\n"

    for f_n, f_s in infos:
        output += f"📄 {f_n} __({humanbytes(f_s)})__\n"

    await message.edit_or_send_as_file(text=output, caption=file_path)
