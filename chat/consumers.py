import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message, Notification
import cloudinary.uploader
import cloudinary.api
import base64
import re


User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            print('unauthorizedkdfjadsh')
            await self.close(code = 1008)    # reject unauthorized
            return
        
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.group_name = f'chat_{self.match_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        sender = self.scope['user']
        if text_data:
            data = json.loads(text_data)
            received_message = data.get('message').strip()
            # media_type = data.get('media_type')
            # media_url = data.get('media_url')       # *

            if not received_message:
                return # ignore empty messages
            
            # save message to db
            message_saved = await database_sync_to_async(Message.objects.create)(
                match_id=self.match_id, 
                sender=sender, 
                text=received_message,
                is_read=False 

            )

            # Broadcast to group
            message = {
                'type': 'chat_message',
                'message': received_message,
                'sender_id': sender.id,
                'media_url': None,
                'media_type': None,
                'created_at': message_saved.created_at.isoformat()
            }
            await self.channel_layer.group_send(
            self.group_name,
            message
            )

    # Channels looks at event['type'] to know which method to call.
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({      # json.dumps is just serializing python dict into json string.
            'message': event['message'],
            'sender_id': event['sender_id'],
            'media_url': event['media_url'],
            'media_type': event['media_type'],
            'created_at': event['created_at']
        }))

# class NotificationConsumer(AsyncWebsocketConsumer):
#     """
#     WebSocket consumer for sending real-time notifications to a user.
#     Each user connects and joins a personal group: 'user_<id>'.
#     """

#     async def connect(self):
#         self.user = self.scope["user"]
#         if self.user.is_authenticated:
#             # Accept the WebSocket connection (handshake completed)
#             await self.accept()

#             # Add this connection to the user's personal group
#             # All notifications for this user will be sent to this group
#             self.group_name = f"user_{self.user.id}"
#             await self.channel_layer.group_add(
#                 self.group_name,
#                 self.channel_name
#             )
#         else:
#             # Close connection if user is not authenticated
#             await self.close()

#     async def disconnect(self, close_code):
#         # Remove the connection from the group on disconnect
#         if hasattr(self, "group_name"):
#             await self.channel_layer.group_discard(
#                 self.group_name,
#                 self.channel_name
#             )

#     async def receive_json(self, content):
#         """
#         Handle incoming messages from the client (optional).
#         Example: mark a notification as read
#         """
#         if content.get("type") == "notification.read":
#             notification_id = content.get("id")
#             await self.mark_as_read(notification_id)

#     @database_sync_to_async
#     def mark_as_read(self, notification_id):
#         # Mark the notification as read in the database
#         try:
#             notif = Notification.objects.get(id=notification_id, recipient=self.user)
#             notif.is_read = True
#             notif.save()
#         except Notification.DoesNotExist:
#             pass

#     async def send_notification(self, event):
#         """
#         This method is called by the channel layer when a notification is sent.
#         It pushes the notification JSON to the client.
#         """
#         await self.send_json({
#             "type": "notification", 
#             "notification_type": event["notification_type"],
#             "content": event["content"],
#             "object_id": event.get("object_id")
#         })