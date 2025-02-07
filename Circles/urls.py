# from django.urls import path, include
# from rest_framework_nested import routers
# from .views import CircleViewSet, CircleMembershipViewSet

# router = routers.SimpleRouter()
# router.register(r'circles', CircleViewSet, basename='circle')

# circles_router = routers.NestedSimpleRouter(router, r'circles', lookup='circle')
# circles_router.register(r'memberships', CircleMembershipViewSet, basename='circle-memberships')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('', include(circles_router.urls)),
# ]