import os
from django.core.files.storage import Storage, default_storage
from django.utils.deconstruct import deconstructible
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger('core.storage')

@deconstructible
class SecureFileStorage(Storage):
    """
    A secure file storage implementation that handles private files by routing
    access through Django views with permission checks.

    This class provides a wrapping interface that can use any of the supported
    storage backends while ensuring secure access to files.
    """
    def __init__(self, private=True, collection='default', base_url=None):
        """
        Initialize the secure storage.

        Args:
            private (bool): Whether files should be served via Django views (True) or
                          direct from storage (False)
            collection (str): A logical grouping for the files (e.g., 'logos', 'avatars')
            base_url (str): Optional base URL for the storage
        """
        self.private = private
        self.collection = collection
        self.base_url = base_url

        # Get the actual storage backend from Django's default_storage
        self.storage = default_storage

    def _get_path(self, name):
        """
        Get the normalized path, prefixed with collection if provided.
        """
        if self.collection and self.collection != 'default':
            # Check if the name already starts with the collection prefix to avoid duplication
            if name.startswith(f"{self.collection}/"):
                return name
            return f"{self.collection}/{name}"
        return name

    def _save(self, name, content):
        """Save the file using the underlying storage"""
        path = self._get_path(name)
        return self.storage._save(path, content)

    def _open(self, name, mode='rb'):
        """Open the file using the underlying storage"""
        path = self._get_path(name)
        return self.storage._open(path, mode)

    def delete(self, name):
        """Delete the file using the underlying storage"""
        path = self._get_path(name)
        return self.storage.delete(path)

    def exists(self, name):
        """Check if the file exists using the underlying storage"""
        path = self._get_path(name)
        return self.storage.exists(path)

    def size(self, name):
        """Get the file size using the underlying storage"""
        path = self._get_path(name)
        return self.storage.size(path)

    def url(self, name):
        """
        Return a URL for the file.

        For private files, return a URL to the Django view that will serve the file
        with permission checks.
        For public files, return a direct URL to the storage backend.
        """
        path = self._get_path(name)

        if self.private:
            # Return URL to Django view for secure file access
            return reverse('serve_protected_file', kwargs={
                'path': path
            })
        else:
            # Return direct URL from storage backend
            if self.base_url:
                # If base_url is provided, use it to construct the URL
                return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
            else:
                # Otherwise, use the storage backend's url method
                return self.storage.url(path)

    def path(self, name):
        """
        Return the file's path on the underlying storage if available
        """
        if hasattr(self.storage, 'path'):
            path = self._get_path(name)
            return self.storage.path(path)
        raise NotImplementedError("This storage doesn't support absolute paths")

    def get_accessed_time(self, name):
        """Get the last accessed time using the underlying storage if available"""
        if hasattr(self.storage, 'get_accessed_time'):
            path = self._get_path(name)
            return self.storage.get_accessed_time(path)
        raise NotImplementedError("This storage doesn't support accessed time")

    def get_created_time(self, name):
        """Get the creation time using the underlying storage if available"""
        if hasattr(self.storage, 'get_created_time'):
            path = self._get_path(name)
            return self.storage.get_created_time(path)
        raise NotImplementedError("This storage doesn't support created time")

    def get_modified_time(self, name):
        """Get the last modified time using the underlying storage if available"""
        if hasattr(self.storage, 'get_modified_time'):
            path = self._get_path(name)
            return self.storage.get_modified_time(path)
        raise NotImplementedError("This storage doesn't support modified time")
