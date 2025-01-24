    # backend/friends/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model

from api.models import User

from Friends.models import FriendRequest
from Friends.serializers import FriendRequestSerializer, FriendListSerializer
from api.serializers import UserSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication



@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def search_users(request):
    """Search for users by username or email"""
    query = request.GET.get('q', '').strip()
    print("Recieved Query:",query)
    if not query:
        return Response({'error': 'Please provide a search query'}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(email__icontains=query)
    ).exclude(id=request.user.id)[:10]  # Limit to 10 results
    serializer = UserSerializer(users, many=True ,context ={'request':request})



    print(users)
    print(serializer.data)
    
    # return Response(users)
    return Response(serializer.data)






@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_friend_request(request, user_id):
    """Send a friend request to another user"""
    try:
        receiver = User.objects.get(id=user_id)
        
        # Check if users are already friends
        if request.user in receiver.followers.all():
            return Response(
                {'error': 'You are already friends with this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if a request already exists
        if FriendRequest.objects.filter(
            sender=request.user,
            receiver=receiver,
            status=FriendRequest.PENDING
        ).exists():
            return Response(
                {'error': 'Friend request already sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        friend_request = FriendRequest.objects.create(
            sender=request.user,
            receiver=receiver
        )
        
        serializer = FriendRequestSerializer(friend_request , context={'request':request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handle_friend_request(request, request_id):
    """Accept or reject a friend request"""
    try:
        friend_request = FriendRequest.objects.get(
            id=request_id,
            receiver=request.user,
            status=FriendRequest.PENDING
        )
        
        action = request.data.get('action')
        
        if action == 'accept':
            friend_request.status = FriendRequest.ACCEPTED
            friend_request.save()
            
            # Add users to each other's followers
            friend_request.sender.following.add(request.user)
            request.user.following.add(friend_request.sender)
            
            return Response({'status': 'Friend request accepted'})
            
        elif action == 'reject':
            friend_request.status = FriendRequest.REJECTED
            friend_request.save()
            return Response({'status': 'Friend request rejected'})
            
        return Response(
            {'error': 'Invalid action'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except FriendRequest.DoesNotExist:
        return Response(
            {'error': 'Friend request not found'},
            status=status.HTTP_404_NOT_FOUND
        )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_friend_requests(request):
    """Get list of pending friend requests"""
    received_requests = FriendRequest.objects.filter(
        receiver=request.user,
        status=FriendRequest.PENDING
    )
    serializer = FriendRequestSerializer(received_requests, many=True , context={'request':request})
    return Response(serializer.data)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_friends(request):
    """Get list of friends"""
    friends = request.user.followers.all()
    serializer = UserSerializer(friends, many=True , context={'request':request})
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_friend(request, user_id):
    """Remove a friend"""
    try:
        friend = User.objects.get(id=user_id)
        
        if friend not in request.user.followers.all():
            return Response(
                {'error': 'User is not your friend'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove users from each other's followers
        friend.following.remove(request.user)
        request.user.following.remove(friend)
        
        return Response({'status': 'Friend removed successfully'})
        
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )