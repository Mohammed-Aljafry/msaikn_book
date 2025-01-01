import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message, Conversation, UserStatus
from django.utils import timezone
import base64
from django.core.files.base import ContentFile

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.update_user_status(True)
            await self.channel_layer.group_add(
                f"user_{self.user.id}",
                self.channel_name
            )

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.update_user_status(False)
            await self.channel_layer.group_discard(
                f"user_{self.user.id}",
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')

        if message_type == 'typing_status':
            await self.handle_typing_status(data)
        elif message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'delete_message':
            await self.handle_delete_message(data)
        elif message_type == 'mark_read':
            await self.handle_mark_read(data)

    async def handle_typing_status(self, data):
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing', False)
        
        await self.update_typing_status(conversation_id, is_typing)
        
        # Notify other user
        conversation = await self.get_conversation(conversation_id)
        other_user = await self.get_other_user(conversation)
        
        await self.channel_layer.group_send(
            f"user_{other_user.id}",
            {
                "type": "typing_notification",
                "user_id": self.user.id,
                "is_typing": is_typing,
                "conversation_id": conversation_id
            }
        )

    async def handle_chat_message(self, data):
        message = data.get('message', '')
        recipient_id = data.get('recipient_id')
        image_data = data.get('image')
        
        if not message and not image_data:
            return
            
        conversation = await self.get_or_create_conversation(recipient_id)
        
        # Create message
        message_obj = await self.create_message(
            conversation=conversation,
            content=message,
            image_data=image_data
        )
        
        # Prepare message data
        message_data = {
            "type": "chat_message",
            "message": message_obj.content,
            "sender_id": self.user.id,
            "conversation_id": conversation.id,
            "timestamp": message_obj.created_at.isoformat(),
            "message_id": message_obj.id
        }
        
        if message_obj.image:
            message_data["image_url"] = message_obj.image.url
            
        # Send to both users
        for user in [self.user.id, int(recipient_id)]:
            await self.channel_layer.group_send(
                f"user_{user}",
                message_data
            )

    async def handle_delete_message(self, data):
        message_id = data.get('message_id')
        if message_id:
            success = await self.delete_message(message_id)
            if success:
                # Notify both users about deleted message
                message_obj = await self.get_message(message_id)
                for user in [message_obj.sender.id, message_obj.receiver.id]:
                    await self.channel_layer.group_send(
                        f"user_{user}",
                        {
                            "type": "message_deleted",
                            "message_id": message_id
                        }
                    )

    async def handle_mark_read(self, data):
        conversation_id = data.get('conversation_id')
        if conversation_id:
            await self.mark_messages_as_read(conversation_id)
            conversation = await self.get_conversation(conversation_id)
            other_user = await self.get_other_user(conversation)
            
            await self.channel_layer.group_send(
                f"user_{other_user.id}",
                {
                    "type": "messages_read",
                    "conversation_id": conversation_id,
                    "reader_id": self.user.id
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def typing_notification(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps(event))

    async def messages_read(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def update_user_status(self, is_online):
        UserStatus.objects.update_or_create(
            user=self.user,
            defaults={'is_online': is_online, 'last_seen': timezone.now()}
        )

    @database_sync_to_async
    def update_typing_status(self, conversation_id, is_typing):
        status, _ = UserStatus.objects.get_or_create(user=self.user)
        status.is_typing = is_typing
        status.typing_in_conversation_id = conversation_id if is_typing else None
        status.save()

    @database_sync_to_async
    def get_or_create_conversation(self, recipient_id):
        recipient = User.objects.get(id=recipient_id)
        conversation = Conversation.objects.filter(
            participants=self.user
        ).filter(
            participants=recipient
        ).first()
        
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(self.user, recipient)
            
        return conversation

    @database_sync_to_async
    def create_message(self, conversation, content='', image_data=None):
        message = Message(
            conversation=conversation,
            sender=self.user,
            receiver=conversation.participants.exclude(id=self.user.id).first(),
            content=content
        )
        
        if image_data:
            # Convert base64 to image file
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_content = ContentFile(base64.b64decode(imgstr), name=f'msg_{conversation.id}_{timezone.now().timestamp()}.{ext}')
            message.image = image_content
            
        message.save()
        return message

    @database_sync_to_async
    def delete_message(self, message_id):
        try:
            message = Message.objects.get(id=message_id, sender=self.user)
            message.is_deleted = True
            message.save()
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_messages_as_read(self, conversation_id):
        Message.objects.filter(
            conversation_id=conversation_id,
            receiver=self.user,
            is_read=False
        ).update(is_read=True)

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        return Conversation.objects.get(id=conversation_id)

    @database_sync_to_async
    def get_message(self, message_id):
        return Message.objects.get(id=message_id)

    @database_sync_to_async
    def get_other_user(self, conversation):
        return conversation.participants.exclude(id=self.user.id).first()
