from rest_framework import serializers
from .models import Circle, CircleMembership
from django.contrib.auth import get_user_model

# User = get_user_model()

class CircleMembershipSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CircleMembership
        fields = ['id', 'user', 'joined_at']

class CircleSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    memberships = CircleMembershipSerializer(many=True, read_only=True)

    class Meta:
        model = Circle
        fields = ['id', 'name', 'owner', 'created_at', 'memberships']