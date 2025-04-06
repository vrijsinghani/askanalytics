from django.urls import path

# Import WebSocket consumers
from apps.websockets.consumers.notification import NotificationConsumer

# Define WebSocket URL patterns
websocket_urlpatterns = [
    # Notification WebSocket
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]
