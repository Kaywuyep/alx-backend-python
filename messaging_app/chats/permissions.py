# pylint: disable=no-member
from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist
from .models import Conversation


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to ensure only authenticated users who are participants
    in a conversation can send, view, update and delete messages.
    """
    def has_permission(self, request, view):
        """
        Check if user is authenticated before checking object permissions.
        """
        # Allow only authenticated users to access the API
        if not request.user or not request.user.is_authenticated:
            return False

        # For POST requests (creating messages), check if user is participant
        if request.method == 'POST':
            conversation_id = request.data.get('conversation')
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                    return request.user in conversation.users.all()
                except (ObjectDoesNotExist, ValueError):
                    return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        Check if authenticated user is a participant in the conversation
        for viewing, updating, or deleting messages.
        """
        # Ensure user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if object is a Message
        if hasattr(obj, 'conversation'):
            # For messages, check if user is participant in the conversation
            return request.user in obj.conversation.users.all()

        # Check if object is a Conversation
        elif hasattr(obj, 'users'):
            # For conversations, check if user is a participant
            return request.user in obj.users.all()

        # Fallback for other objects
        return False


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
