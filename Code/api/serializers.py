# backend/api/serializers.py

from rest_framework import serializers
from .models import User, Post, Comment , Wall
from Circles.models import Circle , CircleMembership

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
    
    # 1) Add this if you want to expose your JSON field:
    # other_res = serializers.JSONField(read_only=True)
    other_res = serializers.SerializerMethodField()



    
    # circle = serializers.PrimaryKeyRelatedField(
    #     queryset=Circle.objects.all(), required=False, allow_null=True
    # )
    
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
            'comments',
            'wall',
            'other_res',
            # 'visibility_type', 'circle',
        )
        read_only_fields = ('id', 'user', 'created_at', 'likes_count', 'is_liked','other_res',)
    
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
    
    def get_other_res(self, obj):
        """
        Convert each 'url' entry in other_res from relative to absolute,
        using request.build_absolute_uri().
        """
        request = self.context.get('request')
        if not obj.other_res:
            return []

        new_res_list = []
        for res_entry in obj.other_res:
            new_entry = dict(res_entry)  # make a copy
            rel_url = new_entry.get('url', '')

            # If we have a request and a relative URL, build an absolute URL
            if request and rel_url:
                abs_url = request.build_absolute_uri(rel_url)
                new_entry['url'] = abs_url

            new_res_list.append(new_entry)

        return new_res_list
    
class WallSerializer(serializers.ModelSerializer):
    thumbnails = serializers.SerializerMethodField()

    class Meta:
        model = Wall
        fields = ['id', 'name', 'thumbnails']

    def get_thumbnails(self, obj):
        request = self.context.get('request')
        return [
            request.build_absolute_uri(thumbnail.image.url) if request else thumbnail.image.url
            for thumbnail in obj.thumbnails.all()
        ]