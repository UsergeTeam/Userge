""" work with paths or files """

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
from typing import Union, List, Tuple, Sequence

from rarfile import RarFile, is_rarfile

from userge import userge, Message, Config, pool
from userge.utils import humanbytes, time_formatter
from userge.utils.exceptions import ProcessCanceled

_LOG = userge.getLogger(__name__)


class _BaseLib:
    """ Base Class for PackLib and SCLib """
    def __init__(self) -> None:
        self._final_file_path = ""
        self._current = 0
        self._total = 0
        self._output = ''
        self._is_canceled = False
        self._is_finished = False

    @property
    def completed_files(self) -> int:
        """ Returns completed files """
        return self._current

    @property
    def total_files(self) -> int:
        """ Returns total files """
        return self._total

    @property
    def percentage(self) -> int:
        """ Returns percentage """
        return int(round((self._current / self._total) * 100, 2))

    @property
    def progress(self) -> str:
        """ Returns progress """
        percentage = self.percentage
        return "[{}{}]".format(
            ''.join((Config.FINISHED_PROGRESS_STR
                     for i in range(floor(percentage / 5)))),
            ''.join((Config.UNFINISHED_PROGRESS_STR
                     for i in range(20 - floor(percentage / 5)))))

    @property
    def canceled(self) -> bool:
        """ Returns True if canceled """
        return self._is_canceled

    @property
    def finished(self) -> bool:
        """ Returns True if finished """
        return self._current == self._total or self._is_finished

    def cancel(self) -> None:
        """ Cancel running thread """
        self._is_canceled = True

    def _finish(self) -> None:
        self._is_finished = True

    @property
    def output(self) -> str:
        """ Returns output """
        return self._output

    @property
    def final_file_path(self) -> str:
        """ Returns final file path """
        return self._final_file_path


class PackLib(_BaseLib):
    """ Class for PACK / UNPACK / LISTPACK (files / folders) """
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        super().__init__()

    def _zip(self,
             p_type: Union[ZipFile, TarFile],
             file_paths: List[str],
             final_file_path: str) -> None:
        root = dirname(self._file_path)
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
                _LOG.exception(z_e)
                self._output = str(z_e)
            finally:
                self._finish()

    def _unpack(self, file_names: List[str]) -> None:
        if is_zipfile(self._file_path):
            u_type = ZipFile
        elif is_rarfile(self._file_path):
            u_type = RarFile
        else:
            u_type = tar_open
        with u_type(self._file_path, 'r') as p_f:
            for file_name in file_names:
                if self._is_canceled:
                    if not self._output:
                        self._output = "`process canceled!`"
                    if not self._is_finished:
                        self._is_finished = True
                    break
                try:
                    p_f.extract(file_name, self._final_file_path)
                except FileExistsError:
                    pass
                except Exception as z_e:
                    self._output = str(z_e)
                    self._is_finished = True
                    break
                else:
                    self._current += 1

    def pack_path(self, tar: bool) -> None:
        """ PACK file path """
        file_paths = []

        def explorer(path: Path) -> None:
            if path.is_file():
                self._total += 1
                file_paths.append(str(path))
            elif path.is_dir():
                for i in path.iterdir():
                    explorer(i)
        explorer(Path(self._file_path))
        file_name = basename(self._file_path)
        if tar:
            file_name += '.tar'
            p_type = tar_open
        else:
            file_name += '.zip'
            p_type = ZipFile
        self._final_file_path = join(Config.DOWN_PATH, file_name)
        pool.submit_thread(self._zip, p_type, file_paths, self._final_file_path)

    def unpack_path(self) -> None:
        """ UNPACK file path """
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
        dir_name = splitext(basename(self._file_path))[0]
        self._final_file_path = join(
            Config.DOWN_PATH, dir_name.replace('.tar', '').replace('.', '_'))
        for f_n_s in chunked_file_names:
            pool.submit_thread(self._unpack, f_n_s)

    def get_info(self) -> Sequence[Tuple[str, int]]:
        """ Returns PACK info """
        if is_zipfile(self._file_path):
            with ZipFile(self._file_path, 'r') as z_f:
                return tuple((z_.filename, z_.file_size) for z_ in z_f.infolist())
        elif is_rarfile(self._file_path):
            with RarFile(self._file_path, 'r') as r_f:
                return tuple((r_.filename, r_.file_size) for r_ in r_f.infolist())
        else:
            with tar_open(self._file_path, 'r') as t_f:
                return tuple((t_.name, t_.size) for t_ in t_f.getmembers())

    @staticmethod
    def is_supported(file_path: str) -> bool:
        """ Returns file is supported or not """
        return is_zipfile(file_path) or is_tarfile(file_path) or is_rarfile(file_path)


class SCLib(_BaseLib):
    """ Class for split / combine files """
    def __init__(self, file_path: str) -> None:
        self._chunk_size = 1024 * 1024
        self._s_time = time()
        self._path = file_path
        self._file_size = 0
        self._cmp_size = 0
        super().__init__()

    @property
    def completed(self) -> int:
        """ Returns completed file size """
        return self._cmp_size

    @property
    def total(self) -> int:
        """ Returns total file size """
        return self._file_size

    @property
    def percentage(self) -> int:
        """ Returns percentage """
        return int(round((self._cmp_size / self._file_size) * 100, 2))

    @property
    def progress(self) -> str:
        """ Returns progress """
        percentage = self.percentage
        return "[{}{}]".format(
            ''.join((Config.FINISHED_PROGRESS_STR
                     for i in range(floor(percentage / 5)))),
            ''.join((Config.UNFINISHED_PROGRESS_STR
                     for i in range(20 - floor(percentage / 5)))))

    @property
    def speed(self) -> float:
        """ Returns speed """
        return int(round(self._cmp_size / (time() - self._s_time), 2))

    @property
    def eta(self) -> str:
        """ Returns eta """
        return time_formatter(
            (self._file_size - self._cmp_size) / self.speed if self.speed else 0)

    def _split_worker(self, times: int) -> None:
        try:
            with open(self._path, "rb") as o_f:
                for self._current in range(self._total):
                    if self._is_canceled:
                        raise ProcessCanceled
                    t_p = join(
                        self._final_file_path,
                        f"{basename(self._path)}.{str(self._current).zfill(5)}")
                    with open(t_p, "wb") as s_f:
                        for _ in range(times):
                            chunk = o_f.read(self._chunk_size)
                            if self._is_canceled:
                                raise ProcessCanceled
                            if not chunk:
                                break
                            s_f.write(chunk)
                            self._cmp_size += len(chunk)
        except ProcessCanceled:
            self._output = "`process canceled!`"
        except Exception as s_e:
            _LOG.exception(s_e)
            self._output = str(s_e)
        finally:
            self._finish()

    def _combine_worker(self, file_list: List[str]) -> None:
        try:
            with open(self._final_file_path, "wb") as o_f:
                for file_path in file_list:
                    if self._is_canceled:
                        raise ProcessCanceled
                    with open(file_path, "rb") as s_f:
                        while True:
                            chunk = s_f.read(self._chunk_size)
                            if self._is_canceled:
                                raise ProcessCanceled
                            if not chunk:
                                break
                            o_f.write(chunk)
                            self._cmp_size += len(chunk)
                    self._current += 1
        except ProcessCanceled:
            self._output = "`process canceled!`"
        except Exception as c_e:
            _LOG.exception(c_e)
            self._output = str(c_e)
        finally:
            self._finish()

    def split(self, split_size: int) -> None:
        """ Split files """
        split_size = int(split_size) * 1024 * 1024
        self._file_size = os.stat(self._path).st_size
        if self._chunk_size > split_size:
            self._chunk_size = split_size
        times = int(ceil(split_size / self._chunk_size))
        self._total = int(ceil(self._file_size / split_size))
        self._final_file_path = join(
            dirname(self._path), f"split_{basename(self._path).replace('.', '_')}")
        if not isdir(self._final_file_path):
            os.makedirs(self._final_file_path)
        pool.submit_thread(self._split_worker, times)

    def combine(self) -> None:
        """ Combine Split files """
        file_name, ext = splitext(basename(self._path))
        self._final_file_path = join(dirname(self._path), file_name)
        file_list = sorted(glob(self._final_file_path + f".{'[0-9]' * len(ext.lstrip('.'))}"))
        self._total = len(file_list)
        self._file_size = sum((os.stat(f_).st_size for f_ in file_list))
        pool.submit_thread(self._combine_worker, file_list)


@userge.on_cmd('ls', about={
    'header': "list directory",
    'usage': "{tr}ls [path]\n{tr}ls -d : default path"}, allow_channels=False)
async def ls_dir(message: Message) -> None:
    """ list dir """
    path = Config.DOWN_PATH if '-d' in message.flags else message.input_str or '.'
    if not exists(path):
        await message.err("path not exists!")
        return
    path_ = Path(path)
    out = f"<b>PATH</b> : <code>{path}</code>\n\n"
    if path_.is_dir():
        folders = ''
        files = ''
        for p_s in sorted(path_.iterdir()):
            if p_s.is_file():
                if str(p_s).endswith((".mp3", ".flac", ".wav", ".m4a")):
                    files += '🎵'
                elif str(p_s).endswith((".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")):
                    files += '📹'
                elif str(p_s).endswith((".zip", ".tar", ".tar.gz", ".rar")):
                    files += '🗜'
                elif str(p_s).endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".webp")):
                    files += '🖼'
                else:
                    files += '📄'
                size = os.stat(str(p_s)).st_size
                files += f" <code>{p_s.name}</code> <i>({humanbytes(size)})</i>\n"
            else:
                folders += f"📁 <code>{p_s.name}</code>\n"
        out += (folders + files) or "<code>empty path!</code>"
    else:
        size = os.stat(str(path_)).st_size
        out += f"📄 <code>{path_.name}</code> <i>({humanbytes(size)})</i>\n"
    await message.edit_or_send_as_file(out, parse_mode='html')


@userge.on_cmd('dset', about={
    'header': "set temporary working directory",
    'usage': "{tr}dset [path / name]"}, allow_channels=False)
async def dset_(message: Message) -> None:
    """ set dir """
    path = message.input_str
    if not path:
        await message.err("missing file path!")
        return
    try:
        if not isdir(path):
            os.makedirs(path)
        Config.DOWN_PATH = path.rstrip('/') + '/'
        await message.edit(f"set `{path}` as **working directory** successfully!", del_in=5)
    except Exception as p_e:
        await message.err(p_e)


@userge.on_cmd('dreset', about={
    'header': "reset to default working directory",
    'usage': "{tr}dreset"}, allow_channels=False)
async def dreset_(message: Message) -> None:
    """ reset dir """
    path = os.environ.get("DOWN_PATH", "downloads").rstrip('/') + '/'
    Config.DOWN_PATH = path
    await message.edit(f"reset **working directory** to `{path}` successfully!", del_in=5)


@userge.on_cmd("dclear", about={
    'header': "Clear the current working directory"}, allow_channels=False)
async def dclear_(message: Message):
    """ clear dir """
    if not isdir(Config.DOWN_PATH):
        await message.edit(
            f'path : `{Config.DOWN_PATH}` not found and just created!', del_in=5)
    else:
        rmtree(Config.DOWN_PATH, True)
        await message.edit(
            f'path : `{Config.DOWN_PATH}` **cleared** successfully!', del_in=5)
    os.makedirs(Config.DOWN_PATH)


@userge.on_cmd('dremove', about={
    'header': "remove a directory or file",
    'usage': "{tr}dremove [path / name]"}, allow_channels=False)
async def dremove_(message: Message) -> None:
    """ remove dir """
    path = message.input_str
    if not path:
        await message.err("missing file path!")
        return
    if not exists(path):
        await message.err("file path not exists!")
        return
    if isfile(path):
        os.remove(path)
    else:
        rmtree(path)
    await message.edit(f"path : `{path}` **removed** successfully!", del_in=5)


@userge.on_cmd('drename ([^|]+)\|([^|]+)', about={  # noqa
    'header': "rename a directory or file",
    'usage': "{tr}drename [path / name] | [new name]"}, allow_channels=False)
async def drename_(message: Message) -> None:
    """ rename dir """
    path = str(message.matches[0].group(1)).strip()
    new_name = str(message.matches[0].group(2)).strip()
    if not exists(path):
        await message.err(f"file path : {path} not exists!")
        return
    new_path = join(dirname(path), new_name)
    os.rename(path, new_path)
    await message.edit(f"path : `{path}` **renamed** to `{new_path}` successfully!", del_in=5)


@userge.on_cmd(r'split (\d+) ([\s\S]+)', about={
    'header': "Split files",
    'usage': "{tr}split [split size (MB)] [file path]",
    'examples': "{tr}split 5 downloads/test.zip"})
async def split_(message: Message) -> None:
    """ split files """
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
    count = 0
    while not s_obj.finished:
        if message.process_is_canceled:
            s_obj.cancel()
        count += 1
        if count >= Config.EDIT_SLEEP_TIMEOUT:
            count = 0
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
        await sleep(1)
    if s_obj.output:
        await message.err(s_obj.output)
    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(
            f"**split** `{file_path}` into `{s_obj.final_file_path}` "
            f"in `{m_s}` seconds.", log=__name__)


@userge.on_cmd('combine', about={
    'header': "Combine split files",
    'usage': "{tr}combine [file path]",
    'examples': "{tr}combine downloads/test.tar.00000"})
async def combine_(message: Message) -> None:
    """ combine split files """
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
    count = 0
    while not c_obj.finished:
        if message.process_is_canceled:
            c_obj.cancel()
        count += 1
        if count >= Config.EDIT_SLEEP_TIMEOUT:
            count = 0
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
        await sleep(1)
    if c_obj.output:
        await message.err(c_obj.output)
    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(
            f"**combined** `{file_path}` into `{c_obj.final_file_path}` "
            f"in `{m_s}` seconds.", log=__name__)


@userge.on_cmd('zip', about={
    'header': "Zip file / folder",
    'usage': "{tr}zip [file path | folder path]"})
async def zip_(message: Message) -> None:
    """ zip files """
    await _pack_helper(message)


@userge.on_cmd('tar', about={
    'header': "Tar file / folder",
    'usage': "{tr}tar [file path | folder path]"})
async def tar_(message: Message) -> None:
    """ tar files """
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
    count = 0
    while not p_obj.finished:
        if message.process_is_canceled:
            p_obj.cancel()
        count += 1
        if count >= Config.EDIT_SLEEP_TIMEOUT:
            count = 0
            await message.try_to_edit(tmp.format(p_obj.progress,
                                                 p_obj.percentage,
                                                 file_path,
                                                 p_obj.final_file_path,
                                                 p_obj.completed_files,
                                                 p_obj.total_files))
        await sleep(1)
    if p_obj.output:
        await message.err(p_obj.output)
    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(
            f"**packed** `{file_path}` into `{p_obj.final_file_path}` "
            f"in `{m_s}` seconds.", log=__name__)


@userge.on_cmd('unpack', about={
    'header': "unpack packed file",
    'usage': "{tr}unpack [file path]",
    'types': ['zip', 'tar', 'rar']})
async def unpack_(message: Message) -> None:
    """ unpack packed file """
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
    count = 0
    while not p_obj.finished:
        if message.process_is_canceled:
            p_obj.cancel()
        count += 1
        if count >= Config.EDIT_SLEEP_TIMEOUT:
            count = 0
            await message.try_to_edit(tmp.format(p_obj.progress,
                                                 p_obj.percentage,
                                                 file_path,
                                                 p_obj.final_file_path,
                                                 p_obj.completed_files,
                                                 p_obj.total_files))
        await sleep(1)
    if p_obj.output:
        await message.err(p_obj.output)
    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(
            f"**unpacked** `{file_path}` into `{p_obj.final_file_path}` "
            f"in `{m_s}` seconds.", log=__name__)


@userge.on_cmd('packinfo', about={
    'header': "File content of the pack",
    'usage': "{tr}packinfo [file path]",
    'types': ['zip', 'tar', 'rar']})
async def packinfo_(message: Message) -> None:
    """ view packed file info """
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
