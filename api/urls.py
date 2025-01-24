
from django.contrib import admin
from django.urls import path
from api import views  


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('posts/', views.create_post, name='create-post'),
    path('feed/', views.get_feed_posts, name='feed-posts'),
    path('posts/<int:pk>/', views.post_detail, name='post-detail'),
    path('posts/<int:pk>/like/', views.like_unlike_post, name='like-unlike-post'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='like-unlike-post'),
]

urlpatterns += [
    path('profile/<str:username>/', views.profile_detail, name='profile-detail'),
    path('profile/<str:username>/follow/', views.follow_user, name='follow-user'),
]


