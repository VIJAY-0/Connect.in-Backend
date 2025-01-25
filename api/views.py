# backend/api/views.py
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny
from .models import User, Post
from .serializers import UserSerializer, PostSerializer  ,CommentSerializer



@api_view(['POST'])
@permission_classes([AllowAny])  # Allow anyone to register
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow anyone to register
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Please provide both username and password'},
                      status=status.HTTP_400_BAD_REQUEST)
    
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



# backend/api/views.py (Add these profile views)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    
    if request.method == 'GET':
        serializer = UserSerializer(user, context={'request': request})
        posts = Post.objects.filter(user=user)
        post_serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response({
            'user': serializer.data,
            'posts': post_serializer.data,
            'posts_count': posts.count(),
            'followers_count': user.followers.count(),
            'following_count': user.following.count(),
            'is_following': request.user in user.followers.all()
        })
    
    elif request.method == 'PUT' and request.user == user:
        serializer = UserSerializer(user, data=request.data, partial=True,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if request.user != user_to_follow:
        if request.user in user_to_follow.followers.all():
            user_to_follow.followers.remove(request.user)
            action = 'unfollowed'
        else:
            user_to_follow.followers.add(request.user)
            action = 'followed'
        return Response({'status': f'Successfully {action}'})
    return Response({'error': 'You cannot follow yourself'}, status=400)








from rest_framework import status
from rest_framework.decorators import (
    api_view, 
    permission_classes, 
    parser_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from .models import Post, User
from .serializers import PostSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_post(request):
    """
    Create a new post with image and caption
    """
    serializer = PostSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        post =serializer.save(user=request.user)
        print(f"Post created. Image path: {post.image.path}")  # Debug print

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feed_posts(request):
    """
    Get posts for user's feed (posts from followed users and own posts)
    """
    # Get posts from users that the current user follows and their own posts
    followed_users = request.user.following.all()
    posts = Post.objects.filter(
        models.Q(user__in=followed_users) #| models.Q(user=request.user)
    ).order_by('-created_at')
    
    serializer = PostSerializer(
        posts, 
        many=True,
        context={'request': request}
    )
    return Response(serializer.data)





@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def post_detail(request, pk):
    """
    Retrieve, update or delete a post
    """
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data)

    # Ensure only the post owner can update or delete
    if post.user != request.user:
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = PostSerializer(
            post,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_unlike_post(request, pk):
    """
    Like or unlike a post
    """
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        action = 'unliked'
    else:
        post.likes.add(request.user)
        action = 'liked'

    serializer = PostSerializer(post, context={'request': request})
    return Response({
        'status': f'Post {action}',
        'post': serializer.data
    })




# backend/api/views.py
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model

User = get_user_model()

def get_user_from_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    try:
        token = auth_header.split(' ')[1]
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        return User.objects.get(id=user_id)
    except (TokenError, User.DoesNotExist, IndexError):
        return None



# backend/api/views.py
from django.http import FileResponse, HttpResponseNotFound
from django.conf import settings
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.core.files.storage import default_storage


@api_view(['GET'])
@permission_classes([AllowAny])
def serve_image(request, folder, filename):
    try:
        # Construct the file path
        file_path = os.path.join(folder, filename)
        absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        # Check if file exists
        if os.path.exists(absolute_path):
            # Open and return the file
            return FileResponse(open(absolute_path, 'rb'), content_type='image/jpeg')
        else:
            return HttpResponseNotFound('Image not found')
    except Exception as e:
        print(f"Error serving image: {str(e)}")
        return HttpResponseNotFound('Error serving image')
    



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        serializer = CommentSerializer(data=request.data,context={'request':request}
                                       )
        
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Post.DoesNotExist:
        return Response(
            {'error': 'Post not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    


    
    
    
    
    
