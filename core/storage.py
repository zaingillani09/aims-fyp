import logging
from django.core.files.storage import Storage, FileSystemStorage
from gdstorage.storage import GoogleDriveStorage

logger = logging.getLogger(__name__)

class FallbackStorage(Storage):
    def __init__(self, *args, **kwargs):
        self.local = FileSystemStorage()
        try:
            self.gdrive = GoogleDriveStorage()
            self.has_gdrive = True
        except Exception as e:
            logger.warning(f"Failed to initialize GoogleDriveStorage: {e}")
            self.has_gdrive = False

    def _save(self, name, content):
        if self.has_gdrive:
            try:
                # Try saving to Google Drive
                return self.gdrive._save(name, content)
            except Exception as e:
                logger.error(f"Google Drive upload failed: {e}. Falling back to local storage.")
        # Fallback to local storage
        return self.local._save(name, content)

    def _open(self, name, mode='rb'):
        if self.local.exists(name):
            return self.local._open(name, mode)
        if self.has_gdrive:
            try:
                return self.gdrive._open(name, mode)
            except Exception:
                pass
        return self.local._open(name, mode)

    def exists(self, name):
        if self.local.exists(name):
            return True
        if self.has_gdrive:
            try:
                return self.gdrive.exists(name)
            except Exception:
                pass
        return False

    def url(self, name):
        if self.local.exists(name):
            return self.local.url(name)
        if self.has_gdrive:
            try:
                url_val = self.gdrive.url(name)
                if url_val:
                    return url_val
            except Exception:
                pass
        return self.local.url(name)

    def delete(self, name):
        if self.local.exists(name):
            self.local.delete(name)
        if self.has_gdrive:
            try:
                self.gdrive.delete(name)
            except Exception:
                pass

    def size(self, name):
        if self.local.exists(name):
            return self.local.size(name)
        if self.has_gdrive:
            try:
                return self.gdrive.size(name)
            except Exception:
                pass
        return 0

    def get_valid_name(self, name):
        return name

    def get_available_name(self, name, max_length=None):
        return name

