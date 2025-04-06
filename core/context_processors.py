from django.conf import settings

def version_context(request):
    """
    Add version information to the template context.
    
    Returns:
        dict: A dictionary containing version information
    """
    try:
        from core.version import VERSION, COMMIT
    except ImportError:
        VERSION = getattr(settings, 'VERSION', '0.0.0')
        COMMIT = getattr(settings, 'COMMIT', 'dev')
        
    return {
        'VERSION': VERSION,
        'COMMIT': COMMIT
    }
