import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message
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
