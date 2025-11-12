from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    sender_full_name = serializers.CharField(source='sender.profile.full_name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'match', 'sender', 'sender_full_name', 'text', 'created_at', 'is_read']

