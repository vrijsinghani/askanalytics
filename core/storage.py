import os
import uuid
from django.core.files.storage import Storage, default_storage
from django.utils.deconstruct import deconstructible
from django.conf import settings
from django.urls import reverse
from django.core.files.base import ContentFile
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

    # Directory operations

    def list_directory(self, path):
        """
        List files and directories in a given path.
        Works with any storage backend.

        Args:
            path: The directory path to list

        Returns:
            A tuple of (directories, files) where each is a list of names
        """
        path = self._get_path(path)

        # Ensure path ends with slash for directory operations
        if path and not path.endswith('/'):
            path = f"{path}/"

        # For storage backends that support listdir directly
        if hasattr(self.storage, 'listdir'):
            try:
                return self.storage.listdir(path)
            except Exception as e:
                logger.error(f"Error listing directory {path} with listdir: {str(e)}")

        # For S3-like storage backends that don't have a reliable listdir
        # but have connection.meta.client for boto3 operations
        if hasattr(self.storage, 'connection') and hasattr(self.storage.connection, 'meta'):
            try:
                s3_client = self.storage.connection.meta.client
                bucket_name = getattr(self.storage, 'bucket_name', None)

                if s3_client and bucket_name:
                    # List objects with the prefix
                    response = s3_client.list_objects_v2(
                        Bucket=bucket_name,
                        Prefix=path,
                        Delimiter='/'
                    )

                    # Extract directories (CommonPrefixes)
                    directories = []
                    for prefix in response.get('CommonPrefixes', []):
                        # Get the directory name without the full path
                        prefix_path = prefix.get('Prefix', '')
                        if prefix_path.startswith(path):
                            # Remove the path prefix and trailing slash
                            dir_name = prefix_path[len(path):].rstrip('/')
                            if dir_name:
                                directories.append(dir_name)

                    # Extract files (Contents)
                    files = []
                    for obj in response.get('Contents', []):
                        key = obj.get('Key', '')
                        if key.startswith(path) and key != path:
                            # Remove the path prefix
                            file_name = key[len(path):]
                            # Only include files in this directory, not in subdirectories
                            if file_name and '/' not in file_name:
                                files.append(file_name)

                    return directories, files
            except Exception as e:
                logger.error(f"Error listing directory {path} with S3 client: {str(e)}")

        # Fallback for other storage backends or if the above methods fail
        # This is less efficient but should work with any storage backend
        try:
            # Try to find all files with this prefix and extract directories
            all_files = self._list_all_files(path)

            directories = set()
            files = []

            for file_path in all_files:
                if file_path.startswith(path):
                    # Get the relative path from the directory
                    rel_path = file_path[len(path):]

                    # Skip empty paths
                    if not rel_path:
                        continue

                    # If the path contains a slash, it's in a subdirectory
                    if '/' in rel_path:
                        # Get the top-level directory
                        dir_name = rel_path.split('/')[0]
                        directories.add(dir_name)
                    else:
                        # It's a file in this directory
                        files.append(rel_path)

            return list(directories), files
        except Exception as e:
            logger.error(f"Error listing directory {path} with fallback method: {str(e)}")
            return [], []

    def _list_all_files(self, prefix):
        """
        List all files with a given prefix.
        This is a helper method for list_directory.

        Args:
            prefix: The prefix to search for

        Returns:
            A list of file paths
        """
        # For S3-like storage backends
        if hasattr(self.storage, 'connection') and hasattr(self.storage.connection, 'meta'):
            try:
                s3_client = self.storage.connection.meta.client
                bucket_name = getattr(self.storage, 'bucket_name', None)

                if s3_client and bucket_name:
                    # List all objects with the prefix
                    paginator = s3_client.get_paginator('list_objects_v2')
                    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

                    all_files = []
                    for page in pages:
                        for obj in page.get('Contents', []):
                            all_files.append(obj.get('Key', ''))

                    return all_files
            except Exception as e:
                logger.error(f"Error listing all files with prefix {prefix}: {str(e)}")

        # For filesystem storage
        if hasattr(self.storage, 'path'):
            try:
                import os
                base_path = self.storage.path('')
                prefix_path = os.path.join(base_path, prefix)

                all_files = []
                for root, dirs, files in os.walk(prefix_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        # Convert to storage path
                        rel_path = os.path.relpath(full_path, base_path)
                        # Normalize path separators
                        rel_path = rel_path.replace(os.sep, '/')
                        all_files.append(rel_path)

                return all_files
            except Exception as e:
                logger.error(f"Error listing all files with prefix {prefix} using filesystem: {str(e)}")

        # Fallback: empty list
        return []

    def directory_exists(self, path):
        """
        Check if a directory exists.
        Works with any storage backend.

        Args:
            path: The directory path to check

        Returns:
            Boolean indicating if directory exists
        """
        path = self._get_path(path)

        # Ensure path ends with slash for directory operations
        if path and not path.endswith('/'):
            path = f"{path}/"

        # For filesystem storage, check if directory exists
        if hasattr(self.storage, 'path'):
            try:
                import os
                dir_path = self.storage.path(path)
                return os.path.isdir(dir_path)
            except Exception as e:
                logger.error(f"Error checking if directory exists using filesystem: {str(e)}")

        # For S3-like storage backends, check if any files exist with this prefix
        try:
            dirs, files = self.list_directory(path)
            return len(dirs) > 0 or len(files) > 0 or self.exists(path)
        except Exception as e:
            logger.error(f"Error checking if directory exists: {str(e)}")

        return False

    def create_directory(self, path):
        """
        Create a directory.
        Works with any storage backend.

        Args:
            path: The directory path to create

        Returns:
            The created directory path
        """
        path = self._get_path(path)

        # Ensure path ends with slash for directory operations
        if path and not path.endswith('/'):
            path = f"{path}/"

        # For filesystem storage, create directory directly
        if hasattr(self.storage, 'path'):
            try:
                import os
                dir_path = self.storage.path(path)
                os.makedirs(dir_path, exist_ok=True)
                return path
            except Exception as e:
                logger.error(f"Error creating directory using filesystem: {str(e)}")

        # For S3-like storage backends, create an empty placeholder file
        try:
            # Create a .keep file in the directory
            keep_file = f"{path}.keep_{uuid.uuid4().hex[:8]}"
            self.storage.save(keep_file, ContentFile(b''))
            return path
        except Exception as e:
            logger.error(f"Error creating directory: {str(e)}")
            raise

    def delete_directory(self, path):
        """
        Delete a directory and all its contents.
        Works with any storage backend.

        Args:
            path: The directory path to delete

        Returns:
            Number of files deleted
        """
        path = self._get_path(path)

        # Ensure path ends with slash for directory operations
        if path and not path.endswith('/'):
            path = f"{path}/"

        # For filesystem storage, use shutil.rmtree
        if hasattr(self.storage, 'path'):
            try:
                import os
                import shutil
                dir_path = self.storage.path(path)

                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    # Count files before deletion
                    file_count = 0
                    for root, dirs, files in os.walk(dir_path):
                        file_count += len(files)

                    # Delete directory
                    shutil.rmtree(dir_path)
                    return file_count
                return 0
            except Exception as e:
                logger.error(f"Error deleting directory using filesystem: {str(e)}")

        # For S3-like storage backends, delete all files with this prefix
        deleted_count = 0
        try:
            # Get all files with this prefix
            all_files = self._list_all_files(path)

            # Delete each file
            for file_path in all_files:
                try:
                    self.storage.delete(file_path)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting file {file_path}: {str(e)}")

            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting directory: {str(e)}")
            return deleted_count

    def batch_delete(self, paths):
        """
        Delete multiple files efficiently.
        Works with any storage backend.

        Args:
            paths: List of file paths to delete

        Returns:
            Number of files deleted
        """
        deleted_count = 0

        # For S3-like storage backends that support batch delete
        if hasattr(self.storage, 'connection') and hasattr(self.storage.connection, 'meta'):
            try:
                s3_client = self.storage.connection.meta.client
                bucket_name = getattr(self.storage, 'bucket_name', None)

                if s3_client and bucket_name and paths:
                    # Prepare objects for deletion
                    objects_to_delete = [{'Key': self._get_path(path)} for path in paths]

                    # Delete in batches of 1000 (S3 limit)
                    for i in range(0, len(objects_to_delete), 1000):
                        batch = objects_to_delete[i:i+1000]
                        response = s3_client.delete_objects(
                            Bucket=bucket_name,
                            Delete={
                                'Objects': batch,
                                'Quiet': True
                            }
                        )

                        # Count deleted objects
                        deleted_count += len(batch) - len(response.get('Errors', []))

                    return deleted_count
            except Exception as e:
                logger.error(f"Error batch deleting files: {str(e)}")
                # Fall back to individual deletion

        # For other storage backends, delete files individually
        for path in paths:
            try:
                path = self._get_path(path)
                if self.storage.exists(path):
                    self.storage.delete(path)
                    deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting file {path}: {str(e)}")

        return deleted_count

    def get_nested_directory_structure(self, root_path):
        """
        Generate a nested directory structure.
        Works with any storage backend.

        Args:
            root_path: The root path to start from

        Returns:
            A list of dictionaries representing the directory structure
        """
        root_path = self._get_path(root_path)

        # Ensure root_path ends with slash for directory operations
        if root_path and not root_path.endswith('/'):
            root_path = f"{root_path}/"

        # Initialize the directory structure with the root directory
        directory_structure = [{
            'name': 'Home',
            'path': '',
            'directories': []
        }]

        try:
            # Get all files from the root path
            all_files = self._list_all_files(root_path)

            # Extract directories from file paths
            directories = set()
            for file_path in all_files:
                if file_path.startswith(root_path):
                    # Get the relative path from the root
                    rel_path = file_path[len(root_path):]

                    # Skip empty paths
                    if not rel_path:
                        continue

                    # Get the directory part of the path
                    dir_path = os.path.dirname(rel_path)

                    # Add this directory and all parent directories
                    current_dir = dir_path
                    while current_dir:
                        directories.add(current_dir)
                        current_dir = os.path.dirname(current_dir)

            # Create a map of all directories
            dir_map = {'': directory_structure[0]}

            # First pass: create all directory objects
            for dir_path in sorted(directories):
                if dir_path:
                    dir_name = os.path.basename(dir_path)
                    dir_map[dir_path] = {
                        'name': dir_name,
                        'path': dir_path,
                        'directories': []
                    }

            # Second pass: build the hierarchy
            for dir_path in sorted(directories):
                if dir_path:
                    parent_path = os.path.dirname(dir_path)
                    # Add this directory to its parent's directories list
                    if parent_path in dir_map:
                        dir_map[parent_path]['directories'].append(dir_map[dir_path])

            return directory_structure
        except Exception as e:
            logger.error(f"Error generating directory structure: {str(e)}")
            # Return a basic structure as fallback
            return directory_structure
