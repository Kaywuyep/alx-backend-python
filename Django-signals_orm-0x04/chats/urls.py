# pylint: disable=no-member
from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import ConversationViewSet, MessageViewSet
from .auth import (
    register_user,
    login_user,
    logout_user,
    user_profile,
    update_profile)

# Create a router and register our viewsets with it
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

# Create nested router for messages within conversations
conversations_router = nested_routers.NestedDefaultRouter(
    router, r'conversations', lookup='conversation')
conversations_router.register(
    r'messages', MessageViewSet, basename='conversation-messages')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', user_profile, name='profile'),
    path('profile/update/', update_profile, name='update-profile'),
]
