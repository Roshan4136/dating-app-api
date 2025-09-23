from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.profile.first_name', read_only=True)


    class Meta:
        model = Message
        fields = ['id', 'match', 'sender', 'sender_name', 'text', 'created_at', 'is_read']

