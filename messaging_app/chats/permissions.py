# pylint: disable=no-member
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only to the owner of the object
        return obj.user == request.user


class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission to only allow conversation
    participants to access messages.
    """

    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        elif hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        return False


class IsMessageOwnerOrConversationParticipant(permissions.BasePermission):
    """
    Custom permission for messages:
        allow message owner and conversation participants.
    """

    def has_object_permission(self, request, view, obj):
        # Allow message sender
        if obj.sender == request.user:
            return True

        # Allow conversation participants
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()

        return False


class CanCreateMessage(permissions.BasePermission):
    """
    Permission to check if user can create a message in a conversation.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            conversation_id = request.data.get('conversation')
            if conversation_id:
                from .models import Conversation
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                    return request.user in conversation.participants.all()
                except Conversation.DoesNotExist:
                    return False
        return True


class IsOwnerOnly(permissions.BasePermission):
    """
    Permission that only allows owners to access their own resources.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'sender'):
            return obj.sender == request.user
        elif hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        return False
