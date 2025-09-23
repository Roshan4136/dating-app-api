from rest_framework import serializers
from .models import Match, Block

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['id', 'user1', 'user2', 'created_at']

class BlockListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.profile.first_name', read_only=True)
    last_name = serializers.CharField(source='user.profile.last_name', read_only=True)
    profile_id = serializers.IntegerField(source='user.profile.id', read_only=True)
    
    class Meta:
        model = Block
        fields = ['id', 'blocker', 'blocked', 'first_name', 'last_name', 'profile_id']