import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
            
        self.notification_group_name = f'notifications_{self.user.id}'
        
        # Join notification group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave notification group
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        pass
    
    async def send_notification(self, event):
        notification_data = event['notification']
        
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification_data
        }))
        
    @database_sync_to_async
    def get_notification_data(self, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id)
            return {
                'id': notification.id,
                'text': notification.text,
                'type': notification.notification_type,
                'sender': {
                    'username': notification.sender.username,
                    'name': notification.sender.get_full_name() or notification.sender.username,
                    'avatar_url': notification.sender.profile.avatar.url if notification.sender.profile.avatar else None
                },
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_read': notification.is_read
            }
        except Notification.DoesNotExist:
            return None
