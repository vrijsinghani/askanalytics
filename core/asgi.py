"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.organizations.middleware import OrganizationMiddlewareAsync, OrganizationSecurityMiddlewareAsync

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import after django setup to avoid AppRegistryNotReady exception
from core.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        OrganizationMiddlewareAsync(
            OrganizationSecurityMiddlewareAsync(
                URLRouter(websocket_urlpatterns)
            )
        )
    ),
})
