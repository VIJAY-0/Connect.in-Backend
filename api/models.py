# backend/api/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Add related_name to the inherited fields to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    # Your custom fields
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers')




# backend/api/models.py (Add these models)
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts/')
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    comments = models.ManyToManyField(User, related_name='comments_posts', blank=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s post - {self.created_at}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s comment on {self.post}"




# class Likes(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.user.username}'s comment on {self.post}"
