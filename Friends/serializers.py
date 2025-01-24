# backend/friends/serializers.py
from rest_framework import serializers
from api.serializers import UserSerializer
from .models import FriendRequest

class FriendRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']
        read_only_fields = ['status']

class FriendListSerializer(serializers.Serializer):
    user = UserSerializer()
    friendship_date = serializers.DateTimeField()