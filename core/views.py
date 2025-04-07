import os
import mimetypes
import json
from django.http import HttpResponse, Http404, FileResponse, JsonResponse
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import connections
from apps.organizations.utils import get_current_organization
import logging
import redis

logger = logging.getLogger('core.views')

# Create a specific logger for the health check endpoint
health_logger = logging.getLogger('core.views.health')

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


def health_check(request):
    """
    Health check endpoint for monitoring and Docker health checks.

    Checks:
    1. Application is running
    2. Database connections
    3. Redis connection

    Returns:
        JsonResponse with health status information
    """
    health_logger.info("Health check requested from %s", request.META.get('REMOTE_ADDR'))

    # Import version information
    try:
        from core.version import VERSION, COMMIT
    except ImportError:
        VERSION = getattr(settings, 'VERSION', 'unknown')
        COMMIT = getattr(settings, 'COMMIT', 'unknown')

    health_status = {
        'status': 'healthy',
        'services': {
            'application': 'healthy',
            'database': 'unknown',
            'redis': 'unknown'
        },
        'version': VERSION,
        'commit': COMMIT
    }
    health_logger.debug("Initial health status: %s", health_status)

    # Check database connections
    try:
        for conn_name in connections:
            connections[conn_name].cursor()
        health_status['services']['database'] = 'healthy'
        health_logger.info("Database connection check: healthy")
    except Exception as e:
        health_status['services']['database'] = 'unhealthy'
        health_status['status'] = 'unhealthy'
        health_logger.error("Health check - Database error: %s", str(e))

    # Check Redis connection
    try:
        redis_host = settings.REDIS_HOST
        redis_port = settings.REDIS_PORT
        r = redis.Redis(host=redis_host, port=redis_port, socket_connect_timeout=2)
        r.ping()
        health_status['services']['redis'] = 'healthy'
        health_logger.info("Redis connection check: healthy")
    except Exception as e:
        health_status['services']['redis'] = 'unhealthy'
        health_status['status'] = 'unhealthy'
        health_logger.error("Health check - Redis error: %s", str(e))

    # Return simple OK response for Docker health checks if all is well
    if request.GET.get('format') == 'simple' and health_status['status'] == 'healthy':
        health_logger.info("Returning simple OK response")
        return HttpResponse("OK")

    # Return detailed JSON response
    health_logger.info("Returning detailed health status: %s", health_status['status'])
    return JsonResponse(health_status)
