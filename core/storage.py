import os
import logging
import mimetypes
import socket
from io import BytesIO
from django.core.files.storage import Storage, FileSystemStorage
from django.conf import settings
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive']

class FallbackStorage(Storage):
    def __init__(self, *args, **kwargs):
        self.local = FileSystemStorage()
        self.has_gdrive = False
        self.folder_id = None
        
        token_path = os.path.join(settings.BASE_DIR, 'token.json')
        token_info = None
        import json
        
        if os.path.exists(token_path):
            try:
                with open(token_path, 'r') as f:
                    token_info = json.load(f)
            except Exception:
                pass
        elif os.getenv('GOOGLE_DRIVE_TOKEN_JSON'):
            try:
                token_info = json.loads(os.getenv('GOOGLE_DRIVE_TOKEN_JSON'))
            except Exception:
                pass

        if token_info:
            orig_timeout = socket.getdefaulttimeout()
            try:
                socket.setdefaulttimeout(3.0)
                creds = Credentials.from_authorized_user_info(token_info, SCOPES)
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    # Update local token.json if we are running locally
                    if os.path.exists(token_path):
                        with open(token_path, 'w') as f:
                            f.write(creds.to_json())
                        
                self.service = build('drive', 'v3', credentials=creds)
                self.has_gdrive = True
                self.folder_id = self._get_folder_id('MEETING MINUTES')
            except Exception as e:
                logger.warning(f"Failed to initialize user Google Drive credentials: {e}")
                self.has_gdrive = False
            finally:
                socket.setdefaulttimeout(orig_timeout)

    def _get_folder_id(self, folder_name):
        try:
            q = f"mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}' and trashed = false"
            results = self.service.files().list(q=q, fields="files(id)").execute()
            files = results.get('files', [])
            if files:
                return files[0]['id']
            meta = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(body=meta, fields='id').execute()
            return folder.get('id')
        except Exception as e:
            logger.error(f"Failed to get/create Google Drive folder ID: {e}")
            return None

    def _save(self, name, content):
        if self.has_gdrive and self.folder_id:
            orig_timeout = socket.getdefaulttimeout()
            try:
                socket.setdefaulttimeout(4.0)
                mime_type, _ = mimetypes.guess_type(name)
                if not mime_type:
                    mime_type = 'application/octet-stream'
                
                filename = os.path.basename(name)
                media = MediaIoBaseUpload(content.file, mimetype=mime_type, resumable=True)
                meta = {
                    'name': filename,
                    'parents': [self.folder_id]
                }
                
                self.service.files().create(
                    body=meta,
                    media_body=media,
                    fields='id'
                ).execute()
                return filename
            except Exception as e:
                logger.error(f"Google Drive upload failed: {e}. Falling back to local storage.")
            finally:
                socket.setdefaulttimeout(orig_timeout)
        
        return self.local._save(name, content)

    def _open(self, name, mode='rb'):
        if self.local.exists(name):
            return self.local._open(name, mode)
        if self.has_gdrive and self.folder_id:
            orig_timeout = socket.getdefaulttimeout()
            try:
                socket.setdefaulttimeout(3.0)
                filename = os.path.basename(name)
                q = f"name = '{filename}' and '{self.folder_id}' in parents and trashed = false"
                results = self.service.files().list(q=q, fields="files(id)").execute()
                files = results.get('files', [])
                if files:
                    file_id = files[0]['id']
                    request = self.service.files().get_media(fileId=file_id)
                    fh = BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        _, done = downloader.next_chunk()
                    fh.seek(0)
                    from django.core.files import File
                    return File(fh, name)
            except Exception:
                pass
            finally:
                socket.setdefaulttimeout(orig_timeout)
        return self.local._open(name, mode)

    def exists(self, name):
        if self.local.exists(name):
            return True
        if self.has_gdrive and self.folder_id:
            orig_timeout = socket.getdefaulttimeout()
            try:
                socket.setdefaulttimeout(2.0)
                filename = os.path.basename(name)
                q = f"name = '{filename}' and '{self.folder_id}' in parents and trashed = false"
                results = self.service.files().list(q=q, fields="files(id)").execute()
                files = results.get('files', [])
                return len(files) > 0
            except Exception:
                pass
            finally:
                socket.setdefaulttimeout(orig_timeout)
        return False

    def url(self, name):
        if self.local.exists(name):
            return self.local.url(name)
        if self.has_gdrive and self.folder_id:
            orig_timeout = socket.getdefaulttimeout()
            try:
                socket.setdefaulttimeout(2.0)
                filename = os.path.basename(name)
                q = f"name = '{filename}' and '{self.folder_id}' in parents and trashed = false"
                results = self.service.files().list(q=q, fields="files(id, webContentLink)").execute()
                files = results.get('files', [])
                if files and files[0].get('webContentLink'):
                    return files[0]['webContentLink']
            except Exception:
                pass
            finally:
                socket.setdefaulttimeout(orig_timeout)
        return self.local.url(name)

    def delete(self, name):
        if self.local.exists(name):
            self.local.delete(name)
        if self.has_gdrive and self.folder_id:
            orig_timeout = socket.getdefaulttimeout()
            try:
                socket.setdefaulttimeout(3.0)
                filename = os.path.basename(name)
                q = f"name = '{filename}' and '{self.folder_id}' in parents and trashed = false"
                results = self.service.files().list(q=q, fields="files(id)").execute()
                files = results.get('files', [])
                if files:
                    file_id = files[0]['id']
                    self.service.files().delete(fileId=file_id).execute()
            except Exception:
                pass
            finally:
                socket.setdefaulttimeout(orig_timeout)

    def size(self, name):
        if self.local.exists(name):
            return self.local.size(name)
        if self.has_gdrive and self.folder_id:
            orig_timeout = socket.getdefaulttimeout()
            try:
                socket.setdefaulttimeout(2.0)
                filename = os.path.basename(name)
                q = f"name = '{filename}' and '{self.folder_id}' in parents and trashed = false"
                results = self.service.files().list(q=q, fields="files(size)").execute()
                files = results.get('files', [])
                if files and files[0].get('size'):
                    return int(files[0]['size'])
            except Exception:
                pass
            finally:
                socket.setdefaulttimeout(orig_timeout)
        return 0

    def get_valid_name(self, name):
        return name

    def get_available_name(self, name, max_length=None):
        return name
