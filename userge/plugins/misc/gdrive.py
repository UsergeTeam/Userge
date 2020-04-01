import os
import io
import time
import math
import pickle
import asyncio
from json import dumps
from threading import Thread
from datetime import datetime
from mimetypes import guess_type
from httplib2 import Http
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import HttpAccessTokenRefreshError, FlowExchangeError
from pyrogram.errors.exceptions import MessageTooLong
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified
from userge import userge, Message, Config, get_collection
from userge.utils import humanbytes, time_formatter, CANCEL_LIST


class ProcessCanceled(Exception):
    """
    Custom Exception to terminate uploading / downloading or copying thread.
    """


class DBase:
    """
    Database Class for GDrive.
    """

    CREDS = ""

    _LOG = userge.getLogger(__name__)
    __GDRIVE_COLLECTION = get_collection("gdrive")

    def __init__(self, id_: str):
        self.__id = id_
        self._LOG.info("Setting GDrive DBase...")
        self.__load_creds()

    @property
    def _creds(self) -> str:
        return self.CREDS

    @_creds.setter
    def _creds(self, creds: str) -> None:
        self.__class__.CREDS = creds

    def __load_creds(self) -> None:

        if not self._creds:
            result = self.__GDRIVE_COLLECTION.find_one({'_id': self.__id}, {'creds': 1})
            self._creds = pickle.loads(result['creds']) if result else None

        if self._creds:
            try:
                self._LOG.info("Refreshing Creds...")
                self._creds.refresh(Http())

            except HttpAccessTokenRefreshError:
                self._clear_creds()

    def _set_creds(self, creds) -> str:

        self._LOG.info("Setting Creds...")
        self._creds = creds

        result = self.__GDRIVE_COLLECTION.update_one(
            {'_id': self.__id}, {"$set": {'creds': pickle.dumps(creds)}}, upsert=True)

        if result.upserted_id:
            return "Creds Added"

        return "Creds Updated"

    def _clear_creds(self) -> str:

        self._creds = ""
        self._LOG.info("Creds Cleared!")

        if self.__GDRIVE_COLLECTION.find_one_and_delete({'_id': self.__id}):
            return "Creds Cleared"

        return "Creds Not Found"


class GDrive(DBase):
    """
    GDrive Class For Search, Upload, Download, Copy, Move, Delete, EmptyTrash, ...
    """

    AUTH_FLOW = None
    PARENT_ID = ""

    __OAUTH_SCOPE = "https://www.googleapis.com/auth/drive"
    __REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
    __G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
    __G_DRIVE_FILE_LINK = "📄 <a href='https://drive.google.com/open?id={}'>{}</a> __({})__"
    __G_DRIVE_FOLDER_LINK = "📁 <a href='https://drive.google.com/drive/folders/{}'>{}</a> " + \
                            "__(folder)__"

    def __init__(self, message: Message) -> None:
        self.__message = message
        self.__progress = None
        self.__completed = 0
        self.__list = 1
        self.__output = None
        self.__is_finished = False
        self.__is_canceled = False

        self._LOG.info("Setting GDrive...")
        super().__init__(message.from_user.id)

    @property
    def _auth_flow(self) -> object:
        return self.AUTH_FLOW

    @_auth_flow.setter
    def _auth_flow(self, flow: object) -> None:
        self.__class__.AUTH_FLOW = flow

    @property
    def _parent_id(self) -> str:
        return self.PARENT_ID or Config.G_DRIVE_PARENT_ID

    @_parent_id.setter
    def _parent_id(self, id_: str) -> None:
        self.__class__.PARENT_ID = id_

    @property
    def __service(self) -> object:
        return build("drive", "v3", credentials=self._creds, cache_discovery=False)

    def __get_file_id(self, filter_str: bool = False) -> tuple:
        link = self.__message.input_str

        if filter_str:
            link = self.__message.filtered_input_str

        link = link.rstrip('export=download').rstrip('&')

        if link.find("/folders/") != -1:
            out = (link.split('/')[-1], "folder")

        elif link.find("/folderview?id=") != -1:
            out = (link.split('/folderview?id=')[-1], "folder")

        elif link.find("open?id=") != -1:
            out = (link.split("open?id=")[-1].strip(), "file")

        elif link.find("uc?id=") != -1:
            out = (link.split("uc?id=")[-1].strip(), "file")

        elif link.find("file/d/") != -1:
            out = (link.split("/")[-1].strip(), "file")

        elif link.find("id=") != -1:
            out = (link.split("=")[-1].strip(), "file")

        elif link.find("view") != -1:
            out = (link.split('/')[-2], "file")

        else:
            out = (link, "unknown")

        return out

    @userge.new_thread
    def __search(self,
                 search_query: str,
                 parent_id: str = "",
                 list_root: bool = False) -> str:

        force = '-f' in self.__message.flags
        pid = parent_id or self._parent_id

        if pid and not force:
            query = f"'{pid}' in parents and (name contains '{search_query}')"
        else:
            query = f"name contains '{search_query}'"

        page_token = None
        limit = int(self.__message.flags.get('-l', 20))
        page_size = limit if limit < 50 else 50
        fields = 'nextPageToken, files(id, name, mimeType, size)'
        results = []
        msg = ""

        while True:
            response = self.__service.files().list(supportsTeamDrives=True,
                                                   includeTeamDriveItems=True,
                                                   q=query, spaces='drive',
                                                   corpora='allDrives',fields=fields,
                                                   pageSize=page_size,
                                                   orderBy='modifiedTime desc',
                                                   pageToken=page_token).execute()

            for file_ in response.get('files', []):

                if len(results) >= limit:
                    break

                if file_.get('mimeType') == self.__G_DRIVE_DIR_MIME_TYPE:
                    msg += self.__G_DRIVE_FOLDER_LINK.format(file_.get('id'), file_.get('name'))
                else:
                    msg += self.__G_DRIVE_FILE_LINK.format(file_.get('id'), file_.get('name'),
                                                           humanbytes(int(file_.get('size', 0))))
                msg += '\n'
                results.append(file_)

            if len(results) >= limit:
                break

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        del results

        if not msg:
            return "`Not Found!`"

        elif parent_id and not force:
            out = f"**List GDrive Folder** : `{parent_id}`\n"

        elif list_root and not force:
            out = f"**List GDrive Root Folder** : `{self._parent_id}`\n"

        else:
            out = f"**GDrive Search Query** : `{search_query}`\n"

        return out + f"**Limit** : `{limit}`\n\n__Results__ : \n\n" + msg

    def __set_permission(self, file_id: str) -> None:

        permissions = {'role': 'reader', 'type': 'anyone'}

        self.__service.permissions().create(fileId=file_id, body=permissions,
                                            supportsTeamDrives=True).execute()

        self._LOG.info(f"Set Permission : {permissions} for Google-Drive File : {file_id}")

    def __upload_file(self, file_path: str, parent_id: str) -> str:

        if self.__is_canceled:
            raise ProcessCanceled

        mime_type = guess_type(file_path)[0] or "text/plain"
        file_name = os.path.basename(file_path)
        body = {"name": file_name, "mimeType": mime_type, "description": "Uploaded using Userge"}

        if parent_id:
            body["parents"] = [parent_id]

        if os.path.getsize(file_path) == 0:
            media_body = MediaFileUpload(file_path, mimetype=mime_type, resumable=False)

            u_file_obj = self.__service.files().create(body=body, media_body=media_body,
                                                       supportsTeamDrives=True).execute()
            file_id = u_file_obj.get("id")

        else:
            media_body = MediaFileUpload(file_path, mimetype=mime_type,
                                         chunksize=50*1024*1024, resumable=True)

            u_file_obj = self.__service.files().create(body=body, media_body=media_body,
                                                       supportsTeamDrives=True)

            c_time = time.time()
            response = None

            while response is None:
                status, response = u_file_obj.next_chunk()

                if self.__is_canceled:
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

                    self.__progress = tmp.format(
                        "".join(["█" for i in range(math.floor(percentage / 5))]),
                        "".join(["░" for i in range(20 - math.floor(percentage / 5))]),
                        round(percentage, 2),
                        file_name,
                        humanbytes(f_size),
                        humanbytes(uploaded),
                        self.__completed,
                        self.__list,
                        humanbytes(speed),
                        time_formatter(eta))

            file_id = response.get("id")

        if not Config.G_DRIVE_IS_TD:
            self.__set_permission(file_id)

        self.__completed += 1

        drive_file = self.__service.files().get(fileId=file_id, fields='id, name, size',
                                                supportsTeamDrives=True).execute()

        file_id = drive_file.get('id')
        file_name = drive_file.get("name")
        file_size = humanbytes(int(drive_file.get('size', 0)))

        self._LOG.info(
            "Created Google-Drive File => Name: {} ID: {} Size: {}".format(
                file_name, file_id, file_size))

        return self.__G_DRIVE_FILE_LINK.format(file_id, file_name, file_size)

    def __create_drive_dir(self, dir_name: str, parent_id: str) -> str:

        if self.__is_canceled:
            raise ProcessCanceled

        body = {"name": dir_name, "mimeType": self.__G_DRIVE_DIR_MIME_TYPE}

        if parent_id:
            body["parents"] = [parent_id]

        file_ = self.__service.files().create(body=body, supportsTeamDrives=True).execute()

        file_id = file_.get("id")
        file_name = file_.get("name")

        if not Config.G_DRIVE_IS_TD:
            self.__set_permission(file_id)

        self.__completed += 1

        self._LOG.info("Created Google-Drive Folder => Name: {} ID: {} ".format(file_name, file_id))

        return file_id

    def __upload_dir(self, input_directory: str, parent_id: str) -> str:

        if self.__is_canceled:
            raise ProcessCanceled

        list_dirs = os.listdir(input_directory)
        if len(list_dirs) == 0:
            return parent_id

        self.__list += len(list_dirs)

        new_id = None
        for item in list_dirs:
            current_file_name = os.path.join(input_directory, item)

            if os.path.isdir(current_file_name):
                current_dir_id = self.__create_drive_dir(item, parent_id)
                new_id = self.__upload_dir(current_file_name, current_dir_id)
            else:
                self.__upload_file(current_file_name, parent_id)
                new_id = parent_id

        return new_id

    def __upload(self, file_name: str) -> None:
        try:
            if os.path.isfile(file_name):
                self.__output = self.__upload_file(file_name, self._parent_id)
            else:
                folder_name = os.path.basename(os.path.abspath(file_name))
                dir_id = self.__create_drive_dir(folder_name, self._parent_id)
                self.__upload_dir(file_name, dir_id)
                self.__output = self.__G_DRIVE_FOLDER_LINK.format(dir_id, folder_name)

        except HttpError as h_e:
            self.__output = h_e

        except ProcessCanceled:
            self.__output = "`Process Canceled!`"

        finally:
            self.__is_finished = True

    def __download_file(self, path: str, name: str, **kwargs) -> None:

        request = self.__service.files().get_media(fileId=kwargs['id'], supportsTeamDrives=True)

        with io.FileIO(os.path.join(path, name), 'wb') as d_obj:
            d_file_obj = MediaIoBaseDownload(d_obj, request, chunksize=100*1024*1024)

            c_time = time.time()
            done = False

            while done is False:
                status, done = d_file_obj.next_chunk()

                if self.__is_canceled:
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

                    self.__progress = tmp.format(
                        "".join(["█" for i in range(math.floor(percentage / 5))]),
                        "".join(["░" for i in range(20 - math.floor(percentage / 5))]),
                        round(percentage, 2),
                        name,
                        humanbytes(f_size),
                        humanbytes(downloaded),
                        self.__completed,
                        self.__list,
                        humanbytes(speed),
                        time_formatter(eta))

        self.__completed += 1
        self._LOG.info(
            "Downloaded Google-Drive File => Name: {} ID: {} ".format(name, kwargs['id']))

    def __list_drive_dir(self, file_id: str) -> list:

        query = f"'{file_id}' in parents and (name contains '*')"
        fields = 'nextPageToken, files(id, name, mimeType)'
        page_token = None
        page_size = 100
        files = []

        while True:
            response = self.__service.files().list(supportsTeamDrives=True,
                                                   includeTeamDriveItems=True,
                                                   q=query, spaces='drive',
                                                   fields=fields, pageToken=page_token,
                                                   pageSize=page_size, corpora='allDrives',
                                                   orderBy='folder, name').execute()

            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)

            if page_token is None:
                break

            if self.__is_canceled:
                raise ProcessCanceled

        return files

    def __create_server_dir(self, current_path: str, folder_name: str) -> str:
        path = os.path.join(current_path, folder_name)

        if not os.path.exists(path):
            os.mkdir(path)

        self._LOG.info("Created Folder => Name: {} ".format(folder_name))
        self.__completed += 1

        return path

    def __download_dir(self, path: str, **kwargs) -> None:

        if self.__is_canceled:
            raise ProcessCanceled

        files = self.__list_drive_dir(kwargs['id'])
        if len(files) == 0:
            return

        self.__list += len(files)

        for file_ in files:
            if file_['mimeType'] == self.__G_DRIVE_DIR_MIME_TYPE:
                path_ = self.__create_server_dir(path, file_['name'])
                self.__download_dir(path_, **file_)
            else:
                self.__download_file(path, **file_)

    def __download(self, file_id: str) -> None:
        try:
            drive_file = self.__service.files().get(fileId=file_id, fields="id, name, mimeType",
                                                    supportsTeamDrives=True).execute()

            if drive_file['mimeType'] == self.__G_DRIVE_DIR_MIME_TYPE:
                path = self.__create_server_dir(Config.DOWN_PATH, drive_file['name'])
                self.__download_dir(path, **drive_file)
            else:
                self.__download_file(Config.DOWN_PATH, **drive_file)

            self.__output = os.path.join(Config.DOWN_PATH, drive_file['name'])

        except HttpError as h_e:
            self.__output = h_e

        except ProcessCanceled:
            self.__output = "`Process Canceled!`"

        finally:
            self.__is_finished = True

    def __copy_file(self, file_id: str, parent_id: str) -> str:

        if self.__is_canceled:
            raise ProcessCanceled

        body = {}
        if parent_id:
            body["parents"] = [parent_id]

        drive_file = self.__service.files().copy(
            body=body, fileId=file_id, supportsTeamDrives=True).execute()

        percentage = (self.__completed / self.__list) * 100

        tmp = \
            "__Copying Files In GDrive...__\n" + \
            "```[{}{}]({}%)```\n" + \
            "**Completed** : `{}/{}`"

        self.__progress = tmp.format(
            "".join(["█" for i in range(math.floor(percentage / 5))]),
            "".join(["░" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2),
            self.__completed,
            self.__list)

        self.__completed += 1

        self._LOG.info(
            "Copied Google-Drive File => Name: {} ID: {} ".format(
                drive_file['name'], drive_file['id']))

        return drive_file['id']

    def __copy_dir(self, file_id: str, parent_id: str) -> str:

        if self.__is_canceled:
            raise ProcessCanceled

        files = self.__list_drive_dir(file_id)
        if len(files) == 0:
            return parent_id

        self.__list += len(files)

        new_id = None
        for file_ in files:
            if file_['mimeType'] == self.__G_DRIVE_DIR_MIME_TYPE:
                dir_id = self.__create_drive_dir(file_['name'], parent_id)
                new_id = self.__copy_dir(file_['id'], dir_id)
            else:
                self.__copy_file(file_['id'], parent_id)
                new_id = parent_id

        return new_id

    def __copy(self, file_id: str) -> None:
        try:
            drive_file = self.__service.files().get(
                fileId=file_id, fields="id, name, mimeType", supportsTeamDrives=True).execute()

            if drive_file['mimeType'] == self.__G_DRIVE_DIR_MIME_TYPE:
                dir_id = self.__create_drive_dir(drive_file['name'], self._parent_id)
                self.__copy_dir(file_id, dir_id)
                ret_id = dir_id
            else:
                ret_id = self.__copy_file(file_id, self._parent_id)

            drive_file = self.__service.files().get(
                fileId=ret_id, fields="id, name, mimeType, size", supportsTeamDrives=True).execute()

            mime_type = drive_file['mimeType']
            file_name = drive_file['name']
            file_id = drive_file['id']

            if mime_type == self.__G_DRIVE_DIR_MIME_TYPE:
                self.__output = self.__G_DRIVE_FOLDER_LINK.format(file_id, file_name)
            else:
                file_size = humanbytes(int(drive_file.get('size', 0)))
                self.__output = self.__G_DRIVE_FILE_LINK.format(file_id, file_name, file_size)

        except HttpError as h_e:
            self.__output = h_e

        except ProcessCanceled:
            self.__output = "`Process Canceled!`"

        finally:
            self.__is_finished = True

    @userge.new_thread
    def __move(self, file_id: str) -> str:

        previous_parents = ",".join(self.__service.files().get(
            fileId=file_id, fields='parents', supportsTeamDrives=True).execute()['parents'])

        drive_file = self.__service.files().update(fileId=file_id,
                                                   addParents=self._parent_id,
                                                   removeParents=previous_parents,
                                                   fields="id, name, mimeType, size, parents",
                                                   supportsTeamDrives=True).execute()

        self._LOG.info(f"Moved file : {file_id} => " + \
                       f"from : {previous_parents} to : {drive_file['parents']} in Google-Drive")

        mime_type = drive_file['mimeType']
        file_name = drive_file['name']
        file_id = drive_file['id']

        if mime_type == self.__G_DRIVE_DIR_MIME_TYPE:
            return self.__G_DRIVE_FOLDER_LINK.format(file_id, file_name)

        file_size = humanbytes(int(drive_file.get('size', 0)))
        return self.__G_DRIVE_FILE_LINK.format(file_id, file_name, file_size)

    @userge.new_thread
    def __delete(self, file_id: str) -> None:

        self.__service.files().delete(fileId=file_id, supportsTeamDrives=True).execute()

        self._LOG.info(f"Deleted Google-Drive File : {file_id}")

    @userge.new_thread
    def __empty_trash(self) -> None:

        self.__service.files().emptyTrash().execute()

        self._LOG.info("Empty Google-Drive Trash")

    @userge.new_thread
    def __get(self, file_id: str) -> str:

        drive_file = self.__service.files().get(fileId=file_id, fields='*',
                                                supportsTeamDrives=True).execute()

        drive_file['size'] = humanbytes(int(drive_file.get('size', 0)))
        drive_file['quotaBytesUsed'] = humanbytes(int(drive_file.get('quotaBytesUsed', 0)))

        drive_file = dumps(drive_file, sort_keys=True, indent=4)
        self._LOG.info("Getting Google-Drive File Details => {}".format(drive_file))

        return drive_file

    @userge.new_thread
    def __get_perms(self, file_id: str) -> str:

        perm_ids = self.__service.files().get(supportsTeamDrives=True, fileId=file_id,
                                              fields="permissionIds").execute()['permissionIds']
        all_perms = {}
        for perm_id in perm_ids:
            perm = self.__service.permissions().get(fileId=file_id, fields='*',
                                                    supportsTeamDrives=True,
                                                    permissionId=perm_id).execute()
            all_perms[perm_id] = perm

        all_perms = dumps(all_perms, sort_keys=True, indent=4)
        self._LOG.info(f"All Permissions: {all_perms} for Google-Drive File : {file_id}")

        return all_perms

    @userge.new_thread
    def __set_perms(self, file_id: str) -> str:

        permissions = {'role': 'reader', 'type': 'anyone'}

        self.__service.permissions().create(fileId=file_id, body=permissions,
                                            supportsTeamDrives=True).execute()

        drive_file = self.__service.files().get(fileId=file_id, supportsTeamDrives=True,
                                                fields="id, name, mimeType, size").execute()

        self._LOG.info(
            f"Set Permission : {permissions} for Google-Drive File : {file_id}\n{drive_file}")

        mime_type = drive_file['mimeType']
        file_name = drive_file['name']
        file_id = drive_file['id']

        if mime_type == self.__G_DRIVE_DIR_MIME_TYPE:
            return self.__G_DRIVE_FOLDER_LINK.format(file_id, file_name)

        file_size = humanbytes(int(drive_file.get('size', 0)))
        return self.__G_DRIVE_FILE_LINK.format(file_id, file_name, file_size)

    @userge.new_thread
    def __del_perms(self, file_id: str) -> str:

        perm_ids = self.__service.files().get(fileId=file_id, supportsTeamDrives=True,
                                              fields="permissionIds").execute()['permissionIds']
        removed_perms = {}
        for perm_id in perm_ids:
            perm = self.__service.permissions().get(fileId=file_id, fields='*',
                                                    supportsTeamDrives=True,
                                                    permissionId=perm_id).execute()

            if perm['role'] != "owner":
                self.__service.permissions().delete(supportsTeamDrives=True, fileId=file_id,
                                                    permissionId=perm_id).execute()
                removed_perms[perm_id] = perm

        removed_perms = dumps(removed_perms, sort_keys=True, indent=4)
        self._LOG.info(
            f"Remove Permission: {removed_perms} for Google-Drive File : {file_id}")

        return removed_perms

    async def setup(self) -> None:
        """
        Setup GDrive.
        """

        if self._creds:
            await self.__message.edit("`Already Setup!`", del_in=5)
        else:
            self._auth_flow = OAuth2WebServerFlow(Config.G_DRIVE_CLIENT_ID,
                                                  Config.G_DRIVE_CLIENT_SECRET,
                                                  self.__OAUTH_SCOPE,
                                                  redirect_uri=self.__REDIRECT_URI)

            reply_string = f"please visit {self._auth_flow.step1_get_authorize_url()} and "
            reply_string += "send back "
            reply_string += "<code>.gconf [auth_code]</code>"

            await self.__message.edit(text=reply_string, disable_web_page_preview=True)

    async def confirm_setup(self) -> None:
        """
        Finalize GDrive setup.
        """

        if self._auth_flow is None:
            await self.__message.edit("Please run `.gsetup` first", del_in=5)
            return

        await self.__message.edit("Checking Auth Code...")
        try:
            cred = self._auth_flow.step2_exchange(self.__message.input_str)

        except FlowExchangeError as c_i:
            await self.__message.err(c_i)

        else:
            self._set_creds(cred)
            self._auth_flow = None

            await self.__message.edit("`Saved GDrive Creds!`", del_in=3)

    async def clear(self) -> None:
        """
        Clear Creds.
        """

        await self.__message.edit(self._clear_creds(), del_in=3)

    async def set_parent(self) -> None:
        """
        Set Parent id.
        """

        file_id, file_type = self.__get_file_id()

        if file_type != "folder":
            await self.__message.err("Please send me a folder link")

        else:
            self._parent_id = file_id

            await self.__message.edit(
                f"Parents set as `{file_id}` successfully", del_in=5)

    async def reset_parent(self) -> None:
        """
        Reset parent id.
        """

        self._parent_id = ""

        await self.__message.edit("`Parents Reset successfully`", del_in=5)

    async def search(self) -> None:
        """
        Search files in GDrive.
        """

        if self._creds:
            await self.__message.edit("`Loading GDrive Search...`")
            try:
                out = await self.__search(self.__message.filtered_input_str)

            except HttpError as h_e:
                await self.__message.err(h_e)
                return

            try:
                await self.__message.edit(out, disable_web_page_preview=True)

            except MessageTooLong:
                await self.__message.send_as_file(
                    out, caption=f"search results for `{self.__message.filtered_input_str}`")

        else:
            await self.__message.edit("Please run `.gsetup` first", del_in=5)

    async def list_folder(self) -> None:
        """
        List files in GDrive folder or root.
        """

        file_id, file_type = self.__get_file_id(filter_str=True)

        if not file_id and not self._parent_id:
            await self.__message.edit("First set parent path by `.gset`", del_in=5)
            return

        if file_id and file_type != "folder":
            await self.__message.err("Please send me a folder link")
            return

        if self._creds:
            await self.__message.edit("`Loading GDrive List...`")

            root = not bool(file_id)

            try:
                out = await self.__search('*', file_id, root)

            except HttpError as h_e:
                await self.__message.err(h_e)
                return

            try:
                await self.__message.edit(out, disable_web_page_preview=True)

            except MessageTooLong:
                await self.__message.send_as_file(
                    out, caption=f"list results for `{file_id}`")

        else:
            await self.__message.edit("Please run `.gsetup` first", del_in=5)

    async def upload(self) -> None:
        """
        Upload file/folder to GDrive.
        """

        if self._creds:
            upload_file_name = self.__message.input_str

            if not os.path.exists(upload_file_name):
                await self.__message.err("invalid file path provided?")
                return

            await self.__message.edit("`Loading GDrive Upload...`")

            Thread(target=self.__upload, args=(upload_file_name,)).start()
            start_t = datetime.now()

            while not self.__is_finished:
                if self.__message.message_id in CANCEL_LIST:
                    self.__is_canceled = True
                    CANCEL_LIST.remove(self.__message.message_id)

                if self.__progress is not None:
                    try:
                        await self.__message.edit(self.__progress)
                    except MessageNotModified:
                        pass

                await asyncio.sleep(3)

            end_t = datetime.now()
            m_s = (end_t - start_t).seconds

            if self.__output is not None and not self.__is_canceled:
                out = f"**Uploaded Successfully** __in {m_s} seconds__\n\n{self.__output}"

            elif self.__output is not None and self.__is_canceled:
                out = self.__output

            else:
                out = "`failed to upload.. check logs?`"

            await self.__message.edit(out, disable_web_page_preview=True)

        else:
            await self.__message.edit("Please run `.gsetup` first", del_in=5)

    async def download(self) -> None:
        """
        Download file/folder from GDrive.
        """

        if self._creds:
            await self.__message.edit("`Loading GDrive Download...`")

            file_id, _ = self.__get_file_id()

            Thread(target=self.__download, args=(file_id,)).start()
            start_t = datetime.now()

            while not self.__is_finished:
                if self.__message.message_id in CANCEL_LIST:
                    self.__is_canceled = True
                    CANCEL_LIST.remove(self.__message.message_id)

                if self.__progress is not None:
                    try:
                        await self.__message.edit(self.__progress)
                    except MessageNotModified:
                        pass

                await asyncio.sleep(3)

            end_t = datetime.now()
            m_s = (end_t - start_t).seconds

            if self.__output is not None and not self.__is_canceled:
                out = f"**Downloaded Successfully** __in {m_s} seconds__\n\n`{self.__output}`"

            elif self.__output is not None and self.__is_canceled:
                out = self.__output

            else:
                out = "`failed to download.. check logs?`"

            await self.__message.edit(out, disable_web_page_preview=True)

        else:
            await self.__message.edit("Please run `.gsetup` first", del_in=5)

    async def copy(self) -> None:
        """
        Copy file/folder in GDrive.
        """

        if not self._parent_id:
            await self.__message.edit("First set parent path by `.gset`", del_in=5)
            return

        if self._creds:
            await self.__message.edit("`Loading GDrive Copy...`")

            file_id, _ = self.__get_file_id()

            Thread(target=self.__copy, args=(file_id,)).start()
            start_t = datetime.now()

            while not self.__is_finished:
                if self.__message.message_id in CANCEL_LIST:
                    self.__is_canceled = True
                    CANCEL_LIST.remove(self.__message.message_id)

                if self.__progress is not None:
                    try:
                        await self.__message.edit(self.__progress)
                    except MessageNotModified:
                        pass

                await asyncio.sleep(3)

            end_t = datetime.now()
            m_s = (end_t - start_t).seconds

            if self.__output is not None and not self.__is_canceled:
                out = f"**Copied Successfully** __in {m_s} seconds__\n\n{self.__output}"

            elif self.__output is not None and self.__is_canceled:
                out = self.__output

            else:
                out = "`failed to copy.. check logs?`"

            await self.__message.edit(out, disable_web_page_preview=True)

        else:
            await self.__message.edit("Please run `.gsetup` first", del_in=5)

    async def move(self) -> None:
        """
        Move file/folder in GDrive.
        """

        if not self._parent_id:
            await self.__message.edit("First set parent path by `.gset`", del_in=5)
            return

        if self._creds:
            await self.__message.edit("`Loading GDrive Move...`")

            file_id, _ = self.__get_file_id()

            try:
                link = await self.__move(file_id)

            except HttpError as h_e:
                await self.__message.err(h_e)

            else:
                await self.__message.edit(
                    f"`{file_id}` **Moved Successfully**\n\n{link}")

        else:
            await self.__message.edit("Please run `.gsetup` first", del_in=5)

    async def delete(self) -> None:
        """
        Delete file/folder in GDrive.
        """

        if self._creds:
            await self.__message.edit("`Loading GDrive Delete...`")

            file_id, _ = self.__get_file_id()

            try:
                await self.__delete(file_id)

            except HttpError as h_e:
                await self.__message.err(h_e)

            else:
                await self.__message.edit(
                    f"`{file_id}` **Deleted Successfully**", del_in=5)

        else:
            await self.__message.edit("Please run `.gsetup` first", del_in=5)

    async def empty(self) -> None:
        """
        Empty GDrive Trash.
        """

        if self._creds:
            await self.__message.edit("`Loading GDrive Empty Trash...`")
            try:
                await self.__empty_trash()

            except HttpError as h_e:
                await self.__message.err(h_e)

            else:
                await self.__message.edit("`Empty the Trash Successfully`", del_in=5)

        else:
            await self.__message.edit("Please run `.gsetup` first", del_in=5)

    async def get(self) -> None:
        """
        Get details for file/folder in GDrive.
        """

        if self._creds:
            await self.__message.edit("`Loading GDrive GetDetails...`")

            file_id, _ = self.__get_file_id()

            try:
                meta_data = await self.__get(file_id)

            except HttpError as h_e:
                await self.__message.err(h_e)
                return

            try:
                out = f"**I Found these Details for** `{file_id}`\n\n{meta_data}"
                await self.__message.edit(out, disable_web_page_preview=True)

            except MessageTooLong:
                await self.__message.send_as_file(
                    meta_data, caption=f"metadata for `{file_id}`")

        else:
            await self.__message.edit("Please run `.gsetup` first", del_in=5)

    async def get_perms(self) -> None:
        """
        Get all Permissions of file/folder in GDrive.
        """

        if self._creds:
            await self.__message.edit("`Loading GDrive GetPermissions...`")

            file_id, _ = self.__get_file_id()

            try:
                out = await self.__get_perms(file_id)

            except HttpError as h_e:
                await self.__message.err(h_e)
                return

            try:
                out = f"**I Found these Permissions for** `{file_id}`\n\n{out}"
                await self.__message.edit(out, disable_web_page_preview=True)

            except MessageTooLong:
                await self.__message.send_as_file(
                    out, caption=f"view perm results for `{file_id}`")

        else:
            await self.__message.edit("Please run `.gsetup` first", del_in=5)

    async def set_perms(self) -> None:
        """
        Set Permissions to file/folder in GDrive.
        """

        if self._creds:
            await self.__message.edit("`Loading GDrive SetPermissions...`")

            file_id, _ = self.__get_file_id()

            try:
                link = await self.__set_perms(file_id)

            except HttpError as h_e:
                await self.__message.err(h_e)

            else:
                out = f"**Set Permissions successfully for** `{file_id}`\n\n{link}"
                await self.__message.edit(out, disable_web_page_preview=True)

        else:
            await self.__message.edit("Please run `.gsetup` first", del_in=5)

    async def del_perms(self) -> None:
        """
        Remove all permisiions of file/folder in GDrive.
        """

        if self._creds:
            await self.__message.edit("`Loading GDrive DelPermissions...`")

            file_id, _ = self.__get_file_id()

            try:
                out = await self.__del_perms(file_id)

            except HttpError as h_e:
                await self.__message.err(h_e)
                return

            try:
                out = "**Removed These Permissions successfully from**" + \
                    f"`{file_id}`\n\n{out}"
                await self.__message.edit(out, disable_web_page_preview=True)

            except MessageTooLong:
                await self.__message.send_as_file(
                    out, caption=f"removed perm results for `{file_id}`")

        else:
            await self.__message.edit("Please run `.gsetup` first", del_in=5)


@userge.on_cmd("gsetup", about="__Setup GDrive Creds__")
async def gsetup_(message: Message):
    """gsetup"""
    await GDrive(message).setup()


@userge.on_cmd("gconf", about="""\
__Confirm GDrive Setup__

**Usage:**

    `.gconf [auth token]`""")
async def gconf_(message: Message):
    """gconf"""
    await GDrive(message).confirm_setup()


@userge.on_cmd("gclear", about="__Clear GDrive Creds__")
async def gclear_(message: Message):
    """gclear"""
    await GDrive(message).clear()


@userge.on_cmd("gset", about="""\
__Set parent id__

    set destination by setting parent_id (root path).
    this path is like working directory :)

**Usage:**

    `.gset [drive folder link]`

    **drive folder link should be like this!**
    ```https://drive.google.com/drive/folders/{file_id}```
    ```https://drive.google.com/drive/folderview?id={file_id}```""")
async def gset_(message: Message):
    """gset"""
    await GDrive(message).set_parent()


@userge.on_cmd("greset", about="__Reset parent id__")
async def greset_(message: Message):
    """greset"""
    await GDrive(message).reset_parent()


@userge.on_cmd("gfind", about="""\
__Search files in GDrive__

**Available Flags:**

    `-l` : add limit to search (default limit 20)
    `-f` : add to do a force search

**Usage:**

    `.gfind [search query]`
    `.gfind -l10 [search query]`""")
async def gfind_(message: Message):
    """gfind"""
    await GDrive(message).search()


@userge.on_cmd("gls", about="""\
__List files in GDrive Folder or Root__

**Usage:**

    `.gls` for view content in root
    `.gls -l10` add limit to it
    `.gls [drive folder link]` (default limit 20)
    `.gls -l10 [drive folder link]` (add limit)

    **drive folder link should be like this!**
    ```https://drive.google.com/drive/folders/{file_id}```
    ```https://drive.google.com/drive/folderview?id={file_id}```""")
async def gls_(message: Message):
    """gls"""
    await GDrive(message).list_folder()


@userge.on_cmd("gup", about="""\
__Upload files to GDrive__

    set destination by setting parent_id,
    use `.gset` to set parent_id (root path).

**Usage:**

    `.gup [file | folder path]`""")
async def gup_(message: Message):
    """gup"""
    await GDrive(message).upload()


@userge.on_cmd("gdown", about="""\
__Download files from GDrive__

**Usage:**

    `.gdown [file_id | file/folder link]`""")
async def gdown_(message: Message):
    """gdown"""
    await GDrive(message).download()


@userge.on_cmd("gcopy", about="""\
__Copy files in GDrive__

    set destination by setting parent_id,
    use `.gset` to set parent_id (root path).

**Usage:**

    `.gcopy [file_id | file/folder link]`""")
async def gcopy_(message: Message):
    """gcopy"""
    await GDrive(message).copy()


@userge.on_cmd("gmove", about="""\
__Move files in GDrive__

    set destination by setting parent_id,
    use `.gset` to set parent_id (root path).

**Usage:**

    `.gmove [file_id | file/folder link]`""")
async def gmove_(message: Message):
    """gmove"""
    await GDrive(message).move()


@userge.on_cmd("gdel", about="""\
__Delete files in GDrive__

**Usage:**

    `.gdel [file_id | file/folder link]`""")
async def gdel_(message: Message):
    """gdel"""
    await GDrive(message).delete()


@userge.on_cmd("gempty", about="""__Empty the Trash__""")
async def gempty_(message: Message):
    """gempty"""
    await GDrive(message).empty()


@userge.on_cmd("gget", about="""\
__Get metadata to given link in GDrive__

**Usage:**

    `.gget [file_id | file/folder link]`""")
async def gget_(message: Message):
    """gget"""
    await GDrive(message).get()


@userge.on_cmd("ggetperm", about="""\
__Get permissions of file/folder in GDrive__

**Usage:**

    `.ggetperm [file_id | file/folder link]`""")
async def ggetperm_(message: Message):
    """ggetperm"""
    await GDrive(message).get_perms()


@userge.on_cmd("gsetperm", about="""\
__Set permissions to file/folder in GDrive__

**Usage:**

    `.gsetperm [file_id | file/folder link]`""")
async def gsetperm_(message: Message):
    """gsetperm"""
    await GDrive(message).set_perms()


@userge.on_cmd("gdelperm", about="""\
__Remove all permissions of file/folder in GDrive__

**Usage:**

    `.gdelperm [file_id | file/folder link]`""")
async def gdelperm_(message: Message):
    """gdelperm"""
    await GDrive(message).del_perms()
