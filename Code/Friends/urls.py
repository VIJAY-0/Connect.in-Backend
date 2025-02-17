# backend/friends/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_users, name='search-users'),
    path('request/send/<int:user_id>/', views.send_friend_request, name='send-friend-request'),
    path('request/handle/<int:request_id>/', views.handle_friend_request, name='handle-friend-request'),
    path('requests/', views.get_friend_requests, name='get-friend-requests'),
    path('list/', views.get_friends, name='get-friends'),
    path('remove/<int:user_id>/', views.remove_friend, name='remove-friend'),
]
