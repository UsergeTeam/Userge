""" manage your gdrive """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import io
import re
import time
import math
import pickle  # nosec
import asyncio
from json import dumps
from functools import wraps
from datetime import datetime
from mimetypes import guess_type
from urllib.parse import quote

from httplib2 import Http
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from oauth2client.client import (
    OAuth2WebServerFlow, HttpAccessTokenRefreshError, FlowExchangeError)

from userge import userge, Message, Config, get_collection, pool
from userge.utils import humanbytes, time_formatter
from userge.utils.exceptions import ProcessCanceled
from userge.plugins.misc.download import url_download, tg_download

_CREDS: object = None
_AUTH_FLOW: object = None
_PARENT_ID = ""
OAUTH_SCOPE = ["https://www.googleapis.com/auth/drive",
               "https://www.googleapis.com/auth/drive.file",
               "https://www.googleapis.com/auth/drive.metadata"]
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
G_DRIVE_FILE_LINK = "📄 <a href='https://drive.google.com/open?id={}'>{}</a> __({})__"
G_DRIVE_FOLDER_LINK = "📁 <a href='https://drive.google.com/drive/folders/{}'>{}</a> __(folder)__"
_GDRIVE_ID = re.compile(
    r'https://drive.google.com/[\w?.&=/]+([-\w]{33}|(?<=[/=])0(?:A[-\w]{17}|B[-\w]{26}))')

_LOG = userge.getLogger(__name__)
_SAVED_SETTINGS = get_collection("CONFIGS")


async def _init() -> None:
    global _CREDS  # pylint: disable=global-statement
    _LOG.debug("Setting GDrive DBase...")
    result = await _SAVED_SETTINGS.find_one({'_id': 'GDRIVE'}, {'creds': 1})
    _CREDS = pickle.loads(result['creds']) if result else None  # nosec


async def _set_creds(creds: object) -> str:
    global _CREDS  # pylint: disable=global-statement
    _LOG.info("Setting Creds...")
    _CREDS = creds
    result = await _SAVED_SETTINGS.update_one(
        {'_id': 'GDRIVE'}, {"$set": {'creds': pickle.dumps(creds)}}, upsert=True)
    if result.upserted_id:
        return "`Creds Added`"
    return "`Creds Updated`"


async def _clear_creds() -> str:
    global _CREDS  # pylint: disable=global-statement
    _CREDS = None
    _LOG.info("Clearing Creds...")
    if await _SAVED_SETTINGS.find_one_and_delete({'_id': 'GDRIVE'}):
        return "`Creds Cleared`"
    return "`Creds Not Found`"


async def _refresh_creds() -> None:
    try:
        _LOG.debug("Refreshing Creds...")
        _CREDS.refresh(Http())
    except HttpAccessTokenRefreshError as h_e:
        _LOG.exception(h_e)
        _LOG.info(await _clear_creds())


def creds_dec(func):
    """ decorator for check CREDS """
    @wraps(func)
    async def wrapper(self):
        # pylint: disable=protected-access
        if _CREDS:
            await _refresh_creds()
            await func(self)
        else:
            await self._message.edit("Please run `.gsetup` first", del_in=5)
    return wrapper


class _GDrive:
    """ GDrive Class For Search, Upload, Download, Copy, Move, Delete, EmptyTrash, ... """
    def __init__(self) -> None:
        self._parent_id = _PARENT_ID or Config.G_DRIVE_PARENT_ID
        self._completed = 0
        self._list = 1
        self._progress = None
        self._output = None
        self._is_canceled = False
        self._is_finished = False

    def _cancel(self) -> None:
        self._is_canceled = True

    def _finish(self) -> None:
        self._is_finished = True

    @property
    def _service(self) -> object:
        return build("drive", "v3", credentials=_CREDS, cache_discovery=False)

    @pool.run_in_thread
    def _search(self,
                search_query: str,
                flags: list,
                parent_id: str = "",
                list_root: bool = False) -> str:
        force = '-f' in flags
        pid = parent_id or self._parent_id
        if pid and not force:
            query = f"'{pid}' in parents and (name contains '{search_query}')"
        else:
            query = f"name contains '{search_query}'"
        page_token = None
        limit = int(flags.get('-l', 20))
        page_size = limit if limit < 50 else 50
        fields = 'nextPageToken, files(id, name, mimeType, size)'
        results = []
        msg = ""
        while True:
            response = self._service.files().list(supportsTeamDrives=True,
                                                  includeTeamDriveItems=True,
                                                  q=query, spaces='drive',
                                                  corpora='allDrives', fields=fields,
                                                  pageSize=page_size,
                                                  orderBy='modifiedTime desc',
                                                  pageToken=page_token).execute()
            for file_ in response.get('files', []):
                if len(results) >= limit:
                    break
                if file_.get('mimeType') == G_DRIVE_DIR_MIME_TYPE:
                    msg += G_DRIVE_FOLDER_LINK.format(file_.get('id'), file_.get('name'))
                else:
                    msg += G_DRIVE_FILE_LINK.format(
                        file_.get('id'), file_.get('name'), humanbytes(int(file_.get('size', 0))))
                msg += '\n'
                results.append(file_)
            if len(results) >= limit:
                break
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        if not msg:
            return "`Not Found!`"
        if parent_id and not force:
            out = f"**List GDrive Folder** : `{parent_id}`\n"
        elif list_root and not force:
            out = f"**List GDrive Root Folder** : `{self._parent_id}`\n"
        else:
            out = f"**GDrive Search Query** : `{search_query}`\n"
        return out + f"**Limit** : `{limit}`\n\n__Results__ : \n\n" + msg

    def _set_permission(self, file_id: str) -> None:
        permissions = {'role': 'reader', 'type': 'anyone'}
        self._service.permissions().create(fileId=file_id, body=permissions,
                                           supportsTeamDrives=True).execute()
        _LOG.info("Set Permission : %s for Google-Drive File : %s", permissions, file_id)

    def _get_file_path(self, file_id: str, file_name: str) -> str:
        tmp_path = [file_name]
        while True:
            response = self._service.files().get(
                fileId=file_id, fields='parents', supportsTeamDrives=True).execute()
            if not response:
                break
            file_id = response['parents'][0]
            response = self._service.files().get(
                fileId=file_id, fields='name', supportsTeamDrives=True).execute()
            tmp_path.append(response['name'])
        return '/'.join(reversed(tmp_path[:-1]))

    def _get_output(self, file_id: str) -> str:
        file_ = self._service.files().get(
            fileId=file_id, fields="id, name, size, mimeType", supportsTeamDrives=True).execute()
        file_id = file_.get('id')
        file_name = file_.get('name')
        file_size = humanbytes(int(file_.get('size', 0)))
        mime_type = file_.get('mimeType')
        if mime_type == G_DRIVE_DIR_MIME_TYPE:
            out = G_DRIVE_FOLDER_LINK.format(file_id, file_name)
        else:
            out = G_DRIVE_FILE_LINK.format(file_id, file_name, file_size)
        if Config.G_DRIVE_INDEX_LINK:
            link = os.path.join(
                Config.G_DRIVE_INDEX_LINK.rstrip('/'),
                quote(self._get_file_path(file_id, file_name)))
            if mime_type == G_DRIVE_DIR_MIME_TYPE:
                link += '/'
            out += f"\n👥 __[Shareable Link]({link})__"
        return out

    def _upload_file(self, file_path: str, parent_id: str) -> str:
        if self._is_canceled:
            raise ProcessCanceled
        mime_type = guess_type(file_path)[0] or "text/plain"
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        body = {"name": file_name, "mimeType": mime_type, "description": "Uploaded using Userge"}
        if parent_id:
            body["parents"] = [parent_id]
        if file_size == 0:
            media_body = MediaFileUpload(file_path, mimetype=mime_type, resumable=False)
            u_file_obj = self._service.files().create(body=body, media_body=media_body,
                                                      supportsTeamDrives=True).execute()
            file_id = u_file_obj.get("id")
        else:
            media_body = MediaFileUpload(file_path, mimetype=mime_type,
                                         chunksize=50*1024*1024, resumable=True)
            u_file_obj = self._service.files().create(body=body, media_body=media_body,
                                                      supportsTeamDrives=True)
            c_time = time.time()
            response = None
            while response is None:
                status, response = u_file_obj.next_chunk(num_retries=5)
                if self._is_canceled:
                    raise ProcessCanceled
                if status:
                    f_size = status.total_size
                    diff = time.time() - c_time
                    uploaded = status.resumable_progress
                    percentage = uploaded / f_size * 100
                    speed = round(uploaded / diff, 2)
                    eta = round((f_size - uploaded) / speed)
                    tmp = \
                        "__Uploading to GDrive...__\n" + \
                        "```[{}{}]({}%)```\n" + \
                        "**File Name** : `{}`\n" + \
                        "**File Size** : `{}`\n" + \
                        "**Uploaded** : `{}`\n" + \
                        "**Completed** : `{}/{}`\n" + \
                        "**Speed** : `{}/s`\n" + \
                        "**ETA** : `{}`"
                    self._progress = tmp.format(
                        "".join((Config.FINISHED_PROGRESS_STR
                                 for _ in range(math.floor(percentage / 5)))),
                        "".join((Config.UNFINISHED_PROGRESS_STR
                                 for _ in range(20 - math.floor(percentage / 5)))),
                        round(percentage, 2),
                        file_name,
                        humanbytes(f_size),
                        humanbytes(uploaded),
                        self._completed,
                        self._list,
                        humanbytes(speed),
                        time_formatter(eta))
            file_id = response.get("id")
        if not Config.G_DRIVE_IS_TD:
            self._set_permission(file_id)
        self._completed += 1
        _LOG.info(
            "Created Google-Drive File => Name: %s ID: %s Size: %s", file_name, file_id, file_size)
        return file_id

    def _create_drive_dir(self, dir_name: str, parent_id: str) -> str:
        if self._is_canceled:
            raise ProcessCanceled
        body = {"name": dir_name, "mimeType": G_DRIVE_DIR_MIME_TYPE}
        if parent_id:
            body["parents"] = [parent_id]
        file_ = self._service.files().create(body=body, supportsTeamDrives=True).execute()
        file_id = file_.get("id")
        file_name = file_.get("name")
        if not Config.G_DRIVE_IS_TD:
            self._set_permission(file_id)
        self._completed += 1
        _LOG.info("Created Google-Drive Folder => Name: %s ID: %s ", file_name, file_id)
        return file_id

    def _upload_dir(self, input_directory: str, parent_id: str) -> str:
        if self._is_canceled:
            raise ProcessCanceled
        list_dirs = os.listdir(input_directory)
        if len(list_dirs) == 0:
            return parent_id
        self._list += len(list_dirs)
        new_id = None
        for item in list_dirs:
            current_file_name = os.path.join(input_directory, item)
            if os.path.isdir(current_file_name):
                current_dir_id = self._create_drive_dir(item, parent_id)
                new_id = self._upload_dir(current_file_name, current_dir_id)
            else:
                self._upload_file(current_file_name, parent_id)
                new_id = parent_id
        return new_id

    def _upload(self, file_name: str) -> None:
        try:
            if os.path.isfile(file_name):
                file_id = self._upload_file(file_name, self._parent_id)
            else:
                folder_name = os.path.basename(os.path.abspath(file_name))
                file_id = self._create_drive_dir(folder_name, self._parent_id)
                self._upload_dir(file_name, file_id)
            self._output = self._get_output(file_id)
        except HttpError as h_e:
            _LOG.exception(h_e)
            self._output = h_e
        except ProcessCanceled:
            self._output = "`Process Canceled!`"
        finally:
            self._finish()

    def _download_file(self, path: str, name: str, **kwargs) -> None:
        request = self._service.files().get_media(fileId=kwargs['id'], supportsTeamDrives=True)
        with io.FileIO(os.path.join(path, name), 'wb') as d_f:
            d_file_obj = MediaIoBaseDownload(d_f, request, chunksize=50*1024*1024)
            c_time = time.time()
            done = False
            while done is False:
                status, done = d_file_obj.next_chunk(num_retries=5)
                if self._is_canceled:
                    raise ProcessCanceled
                if status:
                    f_size = status.total_size
                    diff = time.time() - c_time
                    downloaded = status.resumable_progress
                    percentage = downloaded / f_size * 100
                    speed = round(downloaded / diff, 2)
                    eta = round((f_size - downloaded) / speed)
                    tmp = \
                        "__Downloading From GDrive...__\n" + \
                        "```[{}{}]({}%)```\n" + \
                        "**File Name** : `{}`\n" + \
                        "**File Size** : `{}`\n" + \
                        "**Downloaded** : `{}`\n" + \
                        "**Completed** : `{}/{}`\n" + \
                        "**Speed** : `{}/s`\n" + \
                        "**ETA** : `{}`"
                    self._progress = tmp.format(
                        "".join((Config.FINISHED_PROGRESS_STR
                                 for _ in range(math.floor(percentage / 5)))),
                        "".join((Config.UNFINISHED_PROGRESS_STR
                                 for _ in range(20 - math.floor(percentage / 5)))),
                        round(percentage, 2),
                        name,
                        humanbytes(f_size),
                        humanbytes(downloaded),
                        self._completed,
                        self._list,
                        humanbytes(speed),
                        time_formatter(eta))
        self._completed += 1
        _LOG.info(
            "Downloaded Google-Drive File => Name: %s ID: %s", name, kwargs['id'])

    def _list_drive_dir(self, file_id: str) -> list:
        query = f"'{file_id}' in parents and (name contains '*')"
        fields = 'nextPageToken, files(id, name, mimeType)'
        page_token = None
        page_size = 100
        files = []
        while True:
            response = self._service.files().list(supportsTeamDrives=True,
                                                  includeTeamDriveItems=True,
                                                  q=query, spaces='drive',
                                                  fields=fields, pageToken=page_token,
                                                  pageSize=page_size, corpora='allDrives',
                                                  orderBy='folder, name').execute()
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
            if self._is_canceled:
                raise ProcessCanceled
        return files

    def _create_server_dir(self, current_path: str, folder_name: str) -> str:
        path = os.path.join(current_path, folder_name)
        if not os.path.exists(path):
            os.mkdir(path)
        _LOG.info("Created Folder => Name: %s", folder_name)
        self._completed += 1
        return path

    def _download_dir(self, path: str, **kwargs) -> None:
        if self._is_canceled:
            raise ProcessCanceled
        files = self._list_drive_dir(kwargs['id'])
        if len(files) == 0:
            return
        self._list += len(files)
        for file_ in files:
            if file_['mimeType'] == G_DRIVE_DIR_MIME_TYPE:
                path_ = self._create_server_dir(path, file_['name'])
                self._download_dir(path_, **file_)
            else:
                self._download_file(path, **file_)

    def _download(self, file_id: str) -> None:
        try:
            drive_file = self._service.files().get(fileId=file_id, fields="id, name, mimeType",
                                                   supportsTeamDrives=True).execute()
            if drive_file['mimeType'] == G_DRIVE_DIR_MIME_TYPE:
                path = self._create_server_dir(Config.DOWN_PATH, drive_file['name'])
                self._download_dir(path, **drive_file)
            else:
                self._download_file(Config.DOWN_PATH, **drive_file)
            self._output = os.path.join(Config.DOWN_PATH, drive_file['name'])
        except HttpError as h_e:
            _LOG.exception(h_e)
            self._output = h_e
        except ProcessCanceled:
            self._output = "`Process Canceled!`"
        finally:
            self._finish()

    def _copy_file(self, file_id: str, parent_id: str) -> str:
        if self._is_canceled:
            raise ProcessCanceled
        body = {}
        if parent_id:
            body["parents"] = [parent_id]
        drive_file = self._service.files().copy(
            body=body, fileId=file_id, supportsTeamDrives=True).execute()
        percentage = (self._completed / self._list) * 100
        tmp = \
            "__Copying Files In GDrive...__\n" + \
            "```[{}{}]({}%)```\n" + \
            "**Completed** : `{}/{}`"
        self._progress = tmp.format(
            "".join((Config.FINISHED_PROGRESS_STR
                     for _ in range(math.floor(percentage / 5)))),
            "".join((Config.UNFINISHED_PROGRESS_STR
                     for _ in range(20 - math.floor(percentage / 5)))),
            round(percentage, 2),
            self._completed,
            self._list)
        self._completed += 1
        _LOG.info(
            "Copied Google-Drive File => Name: %s ID: %s", drive_file['name'], drive_file['id'])
        return drive_file['id']

    def _copy_dir(self, file_id: str, parent_id: str) -> str:
        if self._is_canceled:
            raise ProcessCanceled
        files = self._list_drive_dir(file_id)
        if len(files) == 0:
            return parent_id
        self._list += len(files)
        new_id = None
        for file_ in files:
            if file_['mimeType'] == G_DRIVE_DIR_MIME_TYPE:
                dir_id = self._create_drive_dir(file_['name'], parent_id)
                new_id = self._copy_dir(file_['id'], dir_id)
            else:
                self._copy_file(file_['id'], parent_id)
                time.sleep(0.5)  # due to user rate limits
                new_id = parent_id
        return new_id

    def _copy(self, file_id: str) -> None:
        try:
            drive_file = self._service.files().get(
                fileId=file_id, fields="name, mimeType", supportsTeamDrives=True).execute()
            if drive_file['mimeType'] == G_DRIVE_DIR_MIME_TYPE:
                dir_id = self._create_drive_dir(drive_file['name'], self._parent_id)
                self._copy_dir(file_id, dir_id)
                ret_id = dir_id
            else:
                ret_id = self._copy_file(file_id, self._parent_id)
            self._output = self._get_output(ret_id)
        except HttpError as h_e:
            _LOG.exception(h_e)
            self._output = h_e
        except ProcessCanceled:
            self._output = "`Process Canceled!`"
        finally:
            self._finish()

    @pool.run_in_thread
    def _create_drive_folder(self, folder_name: str, parent_id: str) -> str:
        body = {"name": folder_name, "mimeType": G_DRIVE_DIR_MIME_TYPE}
        if parent_id:
            body["parents"] = [parent_id]
        file_ = self._service.files().create(body=body, supportsTeamDrives=True).execute()
        file_id = file_.get("id")
        file_name = file_.get("name")
        if not Config.G_DRIVE_IS_TD:
            self._set_permission(file_id)
        _LOG.info("Created Google-Drive Folder => Name: %s ID: %s ", file_name, file_id)
        return G_DRIVE_FOLDER_LINK.format(file_id, file_name)

    @pool.run_in_thread
    def _move(self, file_id: str) -> str:
        previous_parents = ",".join(self._service.files().get(
            fileId=file_id, fields='parents', supportsTeamDrives=True).execute()['parents'])
        drive_file = self._service.files().update(fileId=file_id,
                                                  addParents=self._parent_id,
                                                  removeParents=previous_parents,
                                                  fields="parents",
                                                  supportsTeamDrives=True).execute()
        _LOG.info("Moved file : %s => "
                  f"from : %s to : {drive_file['parents']} in Google-Drive",
                  file_id, previous_parents)
        return self._get_output(file_id)

    @pool.run_in_thread
    def _delete(self, file_id: str) -> None:
        self._service.files().delete(fileId=file_id, supportsTeamDrives=True).execute()
        _LOG.info("Deleted Google-Drive File : %s", file_id)

    @pool.run_in_thread
    def _empty_trash(self) -> None:
        self._service.files().emptyTrash().execute()
        _LOG.info("Empty Google-Drive Trash")

    @pool.run_in_thread
    def _get(self, file_id: str) -> str:
        drive_file = self._service.files().get(fileId=file_id, fields='*',
                                               supportsTeamDrives=True).execute()
        drive_file['size'] = humanbytes(int(drive_file.get('size', 0)))
        drive_file['quotaBytesUsed'] = humanbytes(int(drive_file.get('quotaBytesUsed', 0)))
        drive_file = dumps(drive_file, sort_keys=True, indent=4)
        _LOG.info("Getting Google-Drive File Details => %s", drive_file)
        return drive_file

    @pool.run_in_thread
    def _get_perms(self, file_id: str) -> str:
        perm_ids = self._service.files().get(supportsTeamDrives=True, fileId=file_id,
                                             fields="permissionIds").execute()['permissionIds']
        all_perms = {}
        for perm_id in perm_ids:
            perm = self._service.permissions().get(fileId=file_id, fields='*',
                                                   supportsTeamDrives=True,
                                                   permissionId=perm_id).execute()
            all_perms[perm_id] = perm
        all_perms = dumps(all_perms, sort_keys=True, indent=4)
        _LOG.info("All Permissions: %s for Google-Drive File : %s", all_perms, file_id)
        return all_perms

    @pool.run_in_thread
    def _set_perms(self, file_id: str) -> str:
        self._set_permission(file_id)
        drive_file = self._service.files().get(fileId=file_id, supportsTeamDrives=True,
                                               fields="id, name, mimeType, size").execute()
        _LOG.info(
            "Set Permission : for Google-Drive File : %s\n%s", file_id, drive_file)
        mime_type = drive_file['mimeType']
        file_name = drive_file['name']
        file_id = drive_file['id']
        if mime_type == G_DRIVE_DIR_MIME_TYPE:
            return G_DRIVE_FOLDER_LINK.format(file_id, file_name)
        file_size = humanbytes(int(drive_file.get('size', 0)))
        return G_DRIVE_FILE_LINK.format(file_id, file_name, file_size)

    @pool.run_in_thread
    def _del_perms(self, file_id: str) -> str:
        perm_ids = self._service.files().get(fileId=file_id, supportsTeamDrives=True,
                                             fields="permissionIds").execute()['permissionIds']
        removed_perms = {}
        for perm_id in perm_ids:
            perm = self._service.permissions().get(fileId=file_id, fields='*',
                                                   supportsTeamDrives=True,
                                                   permissionId=perm_id).execute()
            if perm['role'] != "owner":
                self._service.permissions().delete(supportsTeamDrives=True, fileId=file_id,
                                                   permissionId=perm_id).execute()
                removed_perms[perm_id] = perm
        removed_perms = dumps(removed_perms, sort_keys=True, indent=4)
        _LOG.info(
            "Remove Permission: %s for Google-Drive File : %s", removed_perms, file_id)
        return removed_perms


class Worker(_GDrive):
    """ Worker Class for GDrive """
    def __init__(self, message: Message) -> None:
        self._message = message
        super().__init__()

    def _get_file_id(self, filter_str: bool = False) -> tuple:
        link = self._message.input_str
        if filter_str:
            link = self._message.filtered_input_str
        found = _GDRIVE_ID.search(link)
        if found and 'folder' in link:
            out = (found.group(1), "folder")
        elif found:
            out = (found.group(1), "file")
        else:
            out = (link, "unknown")
        return out

    async def setup(self) -> None:
        """ Setup GDrive """
        global _AUTH_FLOW  # pylint: disable=global-statement
        if _CREDS:
            await self._message.edit("`Already Setup!`", del_in=5)
        else:
            _AUTH_FLOW = OAuth2WebServerFlow(Config.G_DRIVE_CLIENT_ID,
                                             Config.G_DRIVE_CLIENT_SECRET,
                                             OAUTH_SCOPE,
                                             redirect_uri=REDIRECT_URI)
            reply_string = f"please visit {_AUTH_FLOW.step1_get_authorize_url()} and "
            reply_string += "send back "
            reply_string += "<code>.gconf [auth_code]</code>"
            await self._message.edit(
                text=reply_string, disable_web_page_preview=True)

    async def confirm_setup(self) -> None:
        """ Finalize GDrive setup """
        global _AUTH_FLOW  # pylint: disable=global-statement
        if _AUTH_FLOW is None:
            await self._message.edit("Please run `.gsetup` first", del_in=5)
            return
        await self._message.edit("Checking Auth Code...")
        try:
            cred = _AUTH_FLOW.step2_exchange(self._message.input_str)
        except FlowExchangeError as c_i:
            _LOG.exception(c_i)
            await self._message.err(c_i)
        else:
            _AUTH_FLOW = None
            await asyncio.gather(
                _set_creds(cred),
                self._message.edit("`Saved GDrive Creds!`", del_in=3, log=__name__))

    async def clear(self) -> None:
        """ Clear Creds """
        await self._message.edit(await _clear_creds(), del_in=3, log=__name__)

    async def set_parent(self) -> None:
        """ Set Parent id """
        global _PARENT_ID  # pylint: disable=global-statement
        file_id, file_type = self._get_file_id()
        if file_type != "folder":
            await self._message.err("Please send me a folder link")
        else:
            _PARENT_ID = file_id
            await self._message.edit(
                f"Parents set as `{file_id}` successfully", del_in=5)

    async def reset_parent(self) -> None:
        """ Reset parent id """
        global _PARENT_ID  # pylint: disable=global-statement
        _PARENT_ID = ""
        await self._message.edit("`Parents Reset successfully`", del_in=5)

    @creds_dec
    async def share(self) -> None:
        """ get shareable link """
        await self._message.edit("`Loading GDrive Share...`")
        file_id, _ = self._get_file_id()
        try:
            out = await pool.run_in_thread(self._get_output)(file_id)
        except HttpError as h_e:
            _LOG.exception(h_e)
            await self._message.err(h_e._get_reason())  # pylint: disable=protected-access
            return
        await self._message.edit(f"**Shareable Links**\n\n{out}",
                                 disable_web_page_preview=True, log=__name__)

    @creds_dec
    async def search(self) -> None:
        """ Search files in GDrive """
        await self._message.edit("`Loading GDrive Search...`")
        try:
            out = await self._search(
                self._message.filtered_input_str, self._message.flags)
        except HttpError as h_e:
            _LOG.exception(h_e)
            await self._message.err(h_e._get_reason())  # pylint: disable=protected-access
            return
        await self._message.edit_or_send_as_file(
            out, disable_web_page_preview=True,
            caption=f"search results for `{self._message.filtered_input_str}`")

    @creds_dec
    async def make_folder(self) -> None:
        """ Make folder in GDrive parent path """
        if not self._parent_id:
            await self._message.edit("First set parent path by `.gset`", del_in=5)
            return
        if not self._message.input_str:
            await self._message.edit("Please give name for folder", del_in=5)
            return
        try:
            out = await self._create_drive_folder(self._message.input_str, self._parent_id)
        except HttpError as h_e:
            _LOG.exception(h_e)
            await self._message.err(h_e._get_reason())  # pylint: disable=protected-access
            return
        await self._message.edit(f"**Folder Created Successfully**\n\n{out}",
                                 disable_web_page_preview=True, log=__name__)

    @creds_dec
    async def list_folder(self) -> None:
        """ List files in GDrive folder or root """
        file_id, file_type = self._get_file_id(filter_str=True)
        if not file_id and not self._parent_id:
            await self._message.edit("First set parent path by `.gset`", del_in=5)
            return
        if file_id and file_type != "folder":
            await self._message.err("Please send me a folder link")
            return
        await self._message.edit("`Loading GDrive List...`")
        root = not bool(file_id)
        try:
            out = await self._search('*', self._message.flags, file_id, root)
        except HttpError as h_e:
            _LOG.exception(h_e)
            await self._message.err(h_e._get_reason())  # pylint: disable=protected-access
            return
        await self._message.edit_or_send_as_file(
            out, disable_web_page_preview=True, caption=f"list results for `{file_id}`")

    @creds_dec
    async def upload(self) -> None:
        """ Upload from file/folder/link/tg file to GDrive """
        replied = self._message.reply_to_message
        is_url = re.search(
            r"(?:https?|ftp)://[^|\s]+\.[^|\s]+", self._message.input_str)
        dl_loc = ""
        if replied and replied.media:
            try:
                dl_loc, _ = await tg_download(self._message, replied)
            except ProcessCanceled:
                await self._message.edit("`Process Canceled!`", del_in=5)
                return
            except Exception as e_e:
                await self._message.err(e_e)
                return
        elif is_url:
            try:
                dl_loc, _ = await url_download(self._message, self._message.input_str)
            except ProcessCanceled:
                await self._message.edit("`Process Canceled!`", del_in=5)
                return
            except Exception as e_e:
                await self._message.err(e_e)
                return
        file_path = dl_loc if dl_loc else self._message.input_str
        if not os.path.exists(file_path):
            await self._message.err("invalid file path provided?")
            return
        if "|" in file_path:
            file_path, file_name = file_path.split("|")
            new_path = os.path.join(os.path.dirname(file_path.strip()), file_name.strip())
            os.rename(file_path.strip(), new_path)
            file_path = new_path
        await self._message.try_to_edit("`Loading GDrive Upload...`")
        pool.submit_thread(self._upload, file_path)
        start_t = datetime.now()
        count = 0
        while not self._is_finished:
            count += 1
            if self._message.process_is_canceled:
                self._cancel()
            if self._progress is not None and count >= Config.EDIT_SLEEP_TIMEOUT:
                count = 0
                await self._message.try_to_edit(self._progress)
            await asyncio.sleep(1)
        if dl_loc and os.path.exists(dl_loc):
            os.remove(dl_loc)
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        if isinstance(self._output, HttpError):
            out = f"**ERROR** : `{self._output._get_reason()}`"  # pylint: disable=protected-access
        elif self._output is not None and not self._is_canceled:
            out = f"**Uploaded Successfully** __in {m_s} seconds__\n\n{self._output}"
        elif self._output is not None and self._is_canceled:
            out = self._output
        else:
            out = "`failed to upload.. check logs?`"
        await self._message.edit(out, disable_web_page_preview=True, log=__name__)

    @creds_dec
    async def download(self) -> None:
        """ Download file/folder from GDrive """
        await self._message.try_to_edit("`Loading GDrive Download...`")
        file_id, _ = self._get_file_id()
        pool.submit_thread(self._download, file_id)
        start_t = datetime.now()
        count = 0
        while not self._is_finished:
            count += 1
            if self._message.process_is_canceled:
                self._cancel()
            if self._progress is not None and count >= Config.EDIT_SLEEP_TIMEOUT:
                count = 0
                await self._message.try_to_edit(self._progress)
            await asyncio.sleep(1)
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        if isinstance(self._output, HttpError):
            out = f"**ERROR** : `{self._output._get_reason()}`"  # pylint: disable=protected-access
        elif self._output is not None and not self._is_canceled:
            out = f"**Downloaded Successfully** __in {m_s} seconds__\n\n`{self._output}`"
        elif self._output is not None and self._is_canceled:
            out = self._output
        else:
            out = "`failed to download.. check logs?`"
        await self._message.edit(out, disable_web_page_preview=True, log=__name__)

    @creds_dec
    async def copy(self) -> None:
        """ Copy file/folder in GDrive """
        if not self._parent_id:
            await self._message.edit("First set parent path by `.gset`", del_in=5)
            return
        await self._message.try_to_edit("`Loading GDrive Copy...`")
        file_id, _ = self._get_file_id()
        pool.submit_thread(self._copy, file_id)
        start_t = datetime.now()
        count = 0
        while not self._is_finished:
            count += 1
            if self._message.process_is_canceled:
                self._cancel()
            if self._progress is not None and count >= Config.EDIT_SLEEP_TIMEOUT:
                count = 0
                await self._message.try_to_edit(self._progress)
            await asyncio.sleep(1)
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        if isinstance(self._output, HttpError):
            out = f"**ERROR** : `{self._output._get_reason()}`"  # pylint: disable=protected-access
        elif self._output is not None and not self._is_canceled:
            out = f"**Copied Successfully** __in {m_s} seconds__\n\n{self._output}"
        elif self._output is not None and self._is_canceled:
            out = self._output
        else:
            out = "`failed to copy.. check logs?`"
        await self._message.edit(out, disable_web_page_preview=True, log=__name__)

    @creds_dec
    async def move(self) -> None:
        """ Move file/folder in GDrive """
        if not self._parent_id:
            await self._message.edit("First set parent path by `.gset`", del_in=5)
            return
        await self._message.edit("`Loading GDrive Move...`")
        file_id, _ = self._get_file_id()
        try:
            link = await self._move(file_id)
        except HttpError as h_e:
            _LOG.exception(h_e)
            await self._message.err(h_e._get_reason())  # pylint: disable=protected-access
        else:
            await self._message.edit(
                f"`{file_id}` **Moved Successfully**\n\n{link}", log=__name__)

    @creds_dec
    async def delete(self) -> None:
        """ Delete file/folder in GDrive """
        await self._message.edit("`Loading GDrive Delete...`")
        file_id, _ = self._get_file_id()
        try:
            await self._delete(file_id)
        except HttpError as h_e:
            _LOG.exception(h_e)
            await self._message.err(h_e._get_reason())  # pylint: disable=protected-access
        else:
            await self._message.edit(
                f"`{file_id}` **Deleted Successfully**", del_in=5, log=__name__)

    @creds_dec
    async def empty(self) -> None:
        """ Empty GDrive Trash """
        await self._message.edit("`Loading GDrive Empty Trash...`")
        try:
            await self._empty_trash()
        except HttpError as h_e:
            _LOG.exception(h_e)
            await self._message.err(h_e._get_reason())  # pylint: disable=protected-access
        else:
            await self._message.edit(
                "`Empty the Trash Successfully`", del_in=5, log=__name__)

    @creds_dec
    async def get(self) -> None:
        """ Get details for file/folder in GDrive """
        await self._message.edit("`Loading GDrive GetDetails...`")
        file_id, _ = self._get_file_id()
        try:
            meta_data = await self._get(file_id)
        except HttpError as h_e:
            _LOG.exception(h_e)
            await self._message.err(h_e._get_reason())  # pylint: disable=protected-access
            return
        out = f"**I Found these Details for** `{file_id}`\n\n{meta_data}"
        await self._message.edit_or_send_as_file(
            out, disable_web_page_preview=True,
            caption=f"metadata for `{file_id}`")

    @creds_dec
    async def get_perms(self) -> None:
        """ Get all Permissions of file/folder in GDrive """
        await self._message.edit("`Loading GDrive GetPermissions...`")
        file_id, _ = self._get_file_id()
        try:
            out = await self._get_perms(file_id)
        except HttpError as h_e:
            _LOG.exception(h_e)
            await self._message.err(h_e._get_reason())  # pylint: disable=protected-access
            return
        out = f"**I Found these Permissions for** `{file_id}`\n\n{out}"
        await self._message.edit_or_send_as_file(
            out, disable_web_page_preview=True,
            caption=f"view perm results for `{file_id}`")

    @creds_dec
    async def set_perms(self) -> None:
        """ Set Permissions to file/folder in GDrive """
        await self._message.edit("`Loading GDrive SetPermissions...`")
        file_id, _ = self._get_file_id()
        try:
            link = await self._set_perms(file_id)
        except HttpError as h_e:
            _LOG.exception(h_e)
            await self._message.err(h_e._get_reason())  # pylint: disable=protected-access
        else:
            out = f"**Set Permissions successfully for** `{file_id}`\n\n{link}"
            await self._message.edit(out, disable_web_page_preview=True)

    @creds_dec
    async def del_perms(self) -> None:
        """ Remove all permisiions of file/folder in GDrive """
        await self._message.edit("`Loading GDrive DelPermissions...`")
        file_id, _ = self._get_file_id()
        try:
            out = await self._del_perms(file_id)
        except HttpError as h_e:
            _LOG.exception(h_e)
            await self._message.err(h_e._get_reason())  # pylint: disable=protected-access
            return
        out = f"**Removed These Permissions successfully from** `{file_id}`\n\n{out}"
        await self._message.edit_or_send_as_file(
            out, disable_web_page_preview=True,
            caption=f"removed perm results for `{file_id}`")


@userge.on_cmd("gsetup", about={
    'header': "Setup GDrive Creds"})
async def gsetup_(message: Message):
    """ setup creds """
    link = "https://theuserge.github.io/deployment.html#3-g_drive_client_id--g_drive_client_secret"
    if Config.G_DRIVE_CLIENT_ID and Config.G_DRIVE_CLIENT_SECRET:
        if message.chat.id == Config.LOG_CHANNEL_ID:
            await Worker(message).setup()
        else:
            await message.err("try in log channel")
    else:
        await message.edit(
            "`G_DRIVE_CLIENT_ID` and `G_DRIVE_CLIENT_SECRET` not found!\n"
            f"[Read this]({link}) to know more.", disable_web_page_preview=True)


@userge.on_cmd("gconf", about={
    'header': "Confirm GDrive Setup",
    'usage': "{tr}gconf [auth token]"})
async def gconf_(message: Message):
    """ confirm creds """
    await Worker(message).confirm_setup()


@userge.on_cmd("gclear", about={
    'header': "Clear GDrive Creds"})
async def gclear_(message: Message):
    """ clear creds """
    await Worker(message).clear()


@userge.on_cmd("gset", about={
    'header': "Set parent id",
    'description': "set destination by setting parent_id (root path). "
                   "this path is like working directory :)",
    'usage': "{tr}gset [drive folder link]"})
async def gset_(message: Message):
    """ setup path """
    await Worker(message).set_parent()


@userge.on_cmd("greset", about={
    'header': "Reset parent id"})
async def greset_(message: Message):
    """ clear path """
    await Worker(message).reset_parent()


@userge.on_cmd("gfind", about={
    'header': "Search files in GDrive",
    'flags': {
        '-l': "add limit to search (default limit 20)",
        '-f': "add to do a force search"},
    'usage': "{tr}gfind [search query]\n{tr}gfind -l10 [search query]"})
async def gfind_(message: Message):
    """ search files """
    await Worker(message).search()


@userge.on_cmd("gls", about={
    'header': "List files in GDrive Folder or Root",
    'flags': {'-l': "add limit to list (default limit 20)"},
    'usage': "{tr}gls for view content in root\n{tr}gls -l10 add limit to it\n"
             "{tr}gls [drive folder link] (default limit 20)\n"
             "{tr}gls -l10 [drive folder link] (add limit)"})
async def gls_(message: Message):
    """ list files """
    await Worker(message).list_folder()


@userge.on_cmd("gmake", about={
    'header': "Make folders in GDrive parent",
    'usage': "{tr}gmake [folder name]"})
async def gmake_(message: Message):
    """ make folder """
    await Worker(message).make_folder()


@userge.on_cmd("gshare", about={
    'header': "Get Shareable Links for GDrive files",
    'usage': "{tr}gshare [file_id | file/folder link]"})
async def gshare_(message: Message):
    """ share files """
    await Worker(message).share()


@userge.on_cmd("gup", about={
    'header': "Upload files to GDrive",
    'description': "set destination by setting parent_id, "
                   "use `{tr}gset` to set parent_id (root path).",
    'usage': "{tr}gup [file / folder path | direct link | reply to telegram file] "
             "| [new name]",
    'examples': [
        "{tr}gup test.bin : reply to tg file", "{tr}gup downloads/100MB.bin | test.bin",
        "{tr}gup https://speed.hetzner.de/100MB.bin | testing upload.bin"]}, check_downpath=True)
async def gup_(message: Message):
    """ upload to gdrive """
    await Worker(message).upload()


@userge.on_cmd("gdown", about={
    'header': "Download files from GDrive",
    'usage': "{tr}gdown [file_id | file/folder link]"}, check_downpath=True)
async def gdown_(message: Message):
    """ download from gdrive """
    await Worker(message).download()


@userge.on_cmd("gcopy", about={
    'header': "Copy files in GDrive",
    'description': "set destination by setting parent_id, "
                   "use `{tr}gset` to set parent_id (root path).",
    'usage': "{tr}gcopy [file_id | file/folder link]"})
async def gcopy_(message: Message):
    """ copy files in gdrive """
    await Worker(message).copy()


@userge.on_cmd("gmove", about={
    'header': "Move files in GDrive",
    'description': "set destination by setting parent_id, "
                   "use `{tr}gset` to set parent_id (root path).",
    'usage': "{tr}gmove [file_id | file/folder link]"})
async def gmove_(message: Message):
    """ move files in gdrive """
    await Worker(message).move()


@userge.on_cmd("gdel", about={
    'header': "Delete files in GDrive",
    'usage': "{tr}gdel [file_id | file/folder link]"})
async def gdel_(message: Message):
    """ delete files in gdrive """
    await Worker(message).delete()


@userge.on_cmd("gempty", about={
    'header': "Empty the Trash"})
async def gempty_(message: Message):
    """ empty trash """
    await Worker(message).empty()


@userge.on_cmd("gget", about={
    'header': "Get metadata from the given link in GDrive",
    'usage': "{tr}gget [file_id | file/folder link]"})
async def gget_(message: Message):
    """ get details """
    await Worker(message).get()


@userge.on_cmd("ggetperm", about={
    'header': "Get permissions of file/folder in GDrive",
    'usage': "{tr}ggetperm [file_id | file/folder link]"})
async def ggetperm_(message: Message):
    """ get permissions """
    await Worker(message).get_perms()


@userge.on_cmd("gsetperm", about={
    'header': "Set permissions to file/folder in GDrive",
    'usage': "{tr}gsetperm [file_id | file/folder link]"})
async def gsetperm_(message: Message):
    """ set permissions """
    await Worker(message).set_perms()


@userge.on_cmd("gdelperm", about={
    'header': "Remove all permissions of file/folder in GDrive",
    'usage': "{tr}gdelperm [file_id | file/folder link]"})
async def gdelperm_(message: Message):
    """ delete permissions """
    await Worker(message).del_perms()
