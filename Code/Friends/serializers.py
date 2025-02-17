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
    
    
from api.models import User

class SearchUserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating search user responses.
    Includes friend_request_sent to indicate if a request has been sent by the current user.
    """
    friend_request_sent = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'profile_picture',
            'bio',
            'is_following',
            'friend_request_sent',
        )
        extra_kwargs = {
            'email': {'required': False},
            'profile_picture': {'required': False},
            'bio': {'required': False},
        }
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.followers.all()
        return False

    def get_friend_request_sent(self, obj):
        """
        Checks if the currently logged-in user has sent a friend request to the user (`obj`).
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FriendRequest.objects.filter(sender=request.user, receiver=obj).exists()
        return False
