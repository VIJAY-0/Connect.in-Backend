from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


# Circles Model 

class Circle(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, related_name='owned_circles', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

# Circles Model 

class CircleMembership(models.Model):
    circle = models.ForeignKey(Circle, related_name='memberships', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='circle_memberships', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    
    #The unique_together constraint ensures a user can't be added to the same circle more than once.
    class Meta:
        unique_together = ('circle', 'user')

    def __str__(self):
        return f'{self.user.username} in {self.circle.name}'