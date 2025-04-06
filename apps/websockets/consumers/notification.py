import json
import logging
from .base import BaseConsumer

logger = logging.getLogger('websockets.consumers')

class NotificationConsumer(BaseConsumer):
    """
    WebSocket consumer for handling real-time notifications.
    """
    
    async def connect(self):
        """
        Handle WebSocket connection.
        Set up user-specific notification channel.
        """
        # Call parent connect method
        await super().connect()
        
        # Set up user-specific group
        self.user_group_name = f"user_{self.scope['user'].id}_notifications"
        
        # Join user-specific group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        logger.info(f"User {self.scope['user'].username} joined notification channel")
        
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        Clean up user-specific notification channel.
        """
        # Leave user-specific group
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
            
        # Call parent disconnect method
        await super().disconnect(close_code)
        
    async def handle_mark_read(self, data):
        """
        Handle marking notifications as read.
        """
        notification_ids = data.get('notification_ids', [])
        
        if not notification_ids:
            await self.send_error('No notification IDs provided')
            return
            
        # In a real implementation, you would update the database here
        logger.info(f"Marking notifications as read: {notification_ids}")
        
        # Send confirmation
        await self.send_json({
            'type': 'notifications_marked_read',
            'notification_ids': notification_ids
        })
        
    async def notification(self, event):
        """
        Handler for notification messages from channel layer.
        """
        await self.send_json({
            'type': 'notification',
            'notification': event['notification']
        })
