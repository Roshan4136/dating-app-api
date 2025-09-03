# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from match.models import Match
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.room_group_name = f'chat_{self.match_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data['message']
        sender_id = data['sender_id']

        # Save the message to DB
        message = await self.save_message(sender_id, message_text)

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.text,
                'sender_id': message.sender.id,
                'created_at': message.created_at.isoformat()
            }
        )

    # Receive message from group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # DB operation must be async-safe
    @database_sync_to_async
    def save_message(self, sender_id, text):
        sender = User.objects.get(id=sender_id)
        match = Match.objects.get(id=self.match_id)
        return Message.objects.create(
            match=match,
            sender=sender,
            text=text
        )
