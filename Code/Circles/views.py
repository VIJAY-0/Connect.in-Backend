# from django.shortcuts import render

# # Create your views here.
# from rest_framework import viewsets, permissions, status
# from rest_framework.response import Response
# from .models import Circle, CircleMembership
# from .serializers import CircleSerializer, CircleMembershipSerializer
# from django.contrib.auth import get_user_model
# from django.shortcuts import get_object_or_404

# User = get_user_model()

# class CircleViewSet(viewsets.ModelViewSet):
#     queryset = Circle.objects.all()
#     serializer_class = CircleSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         # User can see circles they own or are a member of
#         return Circle.objects.filter(
#             memberships__user=self.request.user
#         ).distinct()

#     def perform_create(self, serializer):
#         circle = serializer.save(owner=self.request.user)
#         CircleMembership.objects.create(circle=circle, user=self.request.user)



# class CircleMembershipViewSet(viewsets.ModelViewSet):
#     queryset = CircleMembership.objects.all()
#     serializer_class = CircleMembershipSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         circle_id = self.kwargs.get('circle_pk')
#         circle = get_object_or_404(Circle, id=circle_id)

#         # Only allow owner to see and manage memberships
#         if circle.owner != self.request.user:
#             return CircleMembership.objects.none()

#         return CircleMembership.objects.filter(circle=circle)

#     def create(self, request, *args, **kwargs):
#         circle_id = self.kwargs.get('circle_pk')
#         circle = get_object_or_404(Circle, id=circle_id)

#         if circle.owner != request.user:
#             return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

#         username = request.data.get('username')
#         if not username:
#             return Response({'username': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         user = get_object_or_404(User, username=username)

#         if CircleMembership.objects.filter(circle=circle, user=user).exists():
#             return Response({'detail': 'User is already a member.'}, status=status.HTTP_400_BAD_REQUEST)

#         CircleMembership.objects.create(circle=circle, user=user)
#         return Response({'detail': 'User added to circle.'}, status=status.HTTP_201_CREATED)

#     def destroy(self, request, *args, **kwargs):
#         circle_id = self.kwargs.get('circle_pk')
#         pk = self.kwargs.get('pk')
#         circle = get_object_or_404(Circle, id=circle_id)

#         if circle.owner != request.user:
#             return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

#         membership = get_object_or_404(CircleMembership, id=pk, circle=circle)
#         # Prevent owner from removing themselves
#         if membership.user == circle.owner:
#             return Response({'detail': 'Cannot remove circle owner.'}, status=status.HTTP_400_BAD_REQUEST)

#         membership.delete()
#         return Response({'detail': 'Member removed from circle.'}, status=status.HTTP_204_NO_CONTENT)