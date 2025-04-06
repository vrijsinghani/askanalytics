import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.organizations.utils import get_current_organization

logger = logging.getLogger('websockets.consumers')

class BaseConsumer(AsyncWebsocketConsumer):
    """
    Base WebSocket consumer that handles common functionality:
    - Authentication
    - Organization context
    - Error handling
    - Message formatting
    """
    
    async def connect(self):
        """
        Handle WebSocket connection.
        Verify authentication and set up channel groups.
        """
        # Check if user is authenticated
        if self.scope["user"].is_anonymous:
            logger.warning("Anonymous user attempted to connect to WebSocket")
            await self.close(code=4003)
            return
            
        # Get organization context
        self.organization = get_current_organization()
        if not self.organization:
            logger.warning(f"User {self.scope['user'].username} connected without organization context")
            
        # Set up channel name
        self.base_group_name = self.get_base_group_name()
        
        # Join base group
        await self.channel_layer.group_add(
            self.base_group_name,
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()
        
        # Send connection confirmation
        await self.send_json({
            'type': 'connection_established',
            'message': 'Connected successfully',
            'user': self.scope["user"].username,
            'organization': str(self.organization.id) if self.organization else None
        })
        
        logger.info(f"WebSocket connection established for user {self.scope['user'].username}")
        
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        Clean up channel groups.
        """
        # Leave base group
        if hasattr(self, 'base_group_name'):
            await self.channel_layer.group_discard(
                self.base_group_name,
                self.channel_name
            )
            
        logger.info(f"WebSocket disconnected for user {self.scope['user'].username} with code {close_code}")
        
    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        Parse JSON and route to appropriate handler.
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if not action:
                await self.send_error('No action specified')
                return
                
            # Route to appropriate handler
            handler_name = f"handle_{action}"
            handler = getattr(self, handler_name, None)
            
            if handler and callable(handler):
                await handler(data)
            else:
                await self.send_error(f"Unknown action: {action}")
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON')
        except Exception as e:
            logger.exception(f"Error handling WebSocket message: {str(e)}")
            await self.send_error(f"Error processing request: {str(e)}")
            
    async def send_json(self, data):
        """
        Send JSON data to the WebSocket.
        """
        await self.send(text_data=json.dumps(data))
        
    async def send_error(self, message):
        """
        Send an error message to the WebSocket.
        """
        await self.send_json({
            'type': 'error',
            'message': message
        })
        
    def get_base_group_name(self):
        """
        Get the base group name for this consumer.
        By default, uses the organization ID if available.
        """
        if self.organization:
            return f"org_{self.organization.id}"
        return "global"
        
    async def broadcast_to_group(self, group_name, message_type, data):
        """
        Broadcast a message to a channel group.
        """
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'broadcast_message',
                'message_type': message_type,
                'data': data
            }
        )
        
    async def broadcast_message(self, event):
        """
        Handler for broadcast messages from channel layer.
        """
        await self.send_json({
            'type': event['message_type'],
            'data': event['data']
        })
