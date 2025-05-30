# from django.shortcuts import render
# Create your views here.
# pylint: disable=no-member
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer
from .serializers import UserSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    Viewset for listing, creating, and retrieving conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show conversations the current user participates in
        return self.queryset.filter(users=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation.
        Expects a list of user IDs in 'user_ids' field.
        """
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response(
                {'error': 'user_ids field is required.'},
                status=status.HTTP_400_BAD_REQUEST
                )

        # Include the current user in the conversation participants
        user_ids.append(request.user.id)
        users = User.objects.filter(id__in=set(user_ids))  # remove duplicates

        conversation = Conversation.objects.create()
        conversation.users.set(users)
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    Viewset for listing and sending messages in conversations.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Optionally filter by conversation ID
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            return self.queryset.filter(conversation_id=conversation_id)
        return self.queryset.none()

    def create(self, request, *args, **kwargs):
        """
        Send a new message in an existing conversation.
        Expects 'conversation_id' and 'content' in request data.
        """
        conversation_id = request.data.get('conversation_id')
        content = request.data.get('content')

        if not conversation_id or not content:
            return Response(
                {'error': 'conversation_id and content fields are required.'},
                status=status.HTTP_400_BAD_REQUEST
                )

        try:
            conversation = Conversation.objects.get(
                id=conversation_id, users=request.user)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found or access denied.'},
                status=status.HTTP_404_NOT_FOUND)

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            content=content
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
