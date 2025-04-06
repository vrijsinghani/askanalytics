import os
import mimetypes
from django.http import HttpResponse, Http404, FileResponse
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.conf import settings
from apps.organizations.utils import get_current_organization
import logging

logger = logging.getLogger('core.views')

@login_required
def serve_protected_file(request, path):
    """
    Serve a file from storage with authentication and authorization checks.
    
    This view is used by SecureFileStorage to serve private files, ensuring
    that only authenticated users with proper permissions can access them.
    
    Args:
        request: The HTTP request
        path: The file path within storage
        
    Returns:
        FileResponse or HttpResponse with the file content
    """
    # Check if file exists
    if not default_storage.exists(path):
        logger.warning(f"Protected file not found: {path}")
        raise Http404("File not found")
    
    # Get organization context
    current_org = get_current_organization()
    
    # Basic organization-based authorization
    # This can be enhanced with more specific permission checks
    if current_org:
        # Check if the file belongs to the current organization
        # This assumes files are stored with organization context in the path
        org_id = str(current_org.id)
        
        # Skip organization check for superusers
        if not request.user.is_superuser:
            # Check if the file path contains organization ID or collection
            # This is a simple check that can be enhanced based on your storage structure
            if org_id not in path and not any(
                path.startswith(collection) for collection in ['user_avatars', 'organization_logos']
            ):
                logger.warning(f"Unauthorized file access attempt: {path} by user {request.user.username}")
                raise Http404("File not found")
    
    try:
        # Get file from storage
        file = default_storage.open(path)
        
        # Determine content type
        content_type, encoding = mimetypes.guess_type(path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # Create response
        response = FileResponse(file, content_type=content_type)
        
        # Set filename for download
        filename = os.path.basename(path)
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        return response
    except Exception as e:
        logger.error(f"Error serving protected file {path}: {str(e)}")
        raise Http404("Error accessing file")
