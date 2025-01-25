# backend/api/serializers.py

from rest_framework import serializers
from .models import User, Post, Comment

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Handles user registration and profile data.
    """
    password = serializers.CharField(write_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'profile_picture',
            'bio',
            'followers_count',
            'following_count',
            'is_following',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'profile_picture': {'required': False},
            'bio': {'required': False}
        }
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.followers.all()
        return False

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'user',
            'text',
            'created_at'
        )
        read_only_fields = ('id', 'user', 'created_at')

class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.
    Includes nested comments and user data.
    """
    user = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only = True)
    is_liked = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id',
            'user',
            'image',
            'image_url',
            'caption',
            'created_at',
            'likes_count',
            'is_liked',
            'comments'
        )
        read_only_fields = ('id', 'user', 'created_at', 'likes_count', 'is_liked')
    
    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)