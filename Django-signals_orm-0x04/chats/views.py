# pylint: disable=no-member
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
# from django.db.models import Q
from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer
from .serializers import MessageSerializer
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter
from .pagination import MessagePagination


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model with basic CRUD operations.
    Only authenticated users can access.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter users based on current user's conversations
        to protect user privacy.
        """
        user = self.request.user
        # Get users who are in conversations with the current user
        user_conversations = Conversation.objects.filter(users=user)
        conversation_users = User.objects.filter(
            conversation__in=user_conversations
        ).distinct()
        return conversation_users

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's profile.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversation model with custom permissions.
    Only participants can access their conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        """
        Return only conversations where the current user is a participant.
        """
        user = self.request.user
        return Conversation.objects.filter(users=user).distinct()

    def perform_create(self, serializer):
        """
        Automatically add the creator to the conversation participants.
        """
        conversation = serializer.save()
        conversation.users.add(self.request.user)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """
        Add a participant to the conversation.
        Only existing participants can add new ones.
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_add = User.objects.get(id=user_id)
            if user_to_add not in conversation.users.all():
                conversation.users.add(user_to_add)
                return Response(
                    {'message': f'User {user_to_add.username} added to conversation'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'message': 'User is already a participant'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """
        Remove a participant from the conversation.
        Only existing participants can remove others (or themselves).
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_to_remove = User.objects.get(id=user_id)
            if user_to_remove in conversation.users.all():
                conversation.users.remove(user_to_remove)
                return Response(
                    {'message': f'User {user_to_remove.username} removed from conversation'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'message': 'User is not a participant'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message model with strict participant-only access.
    Only conversation participants can send, view, update, and delete messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filterset_class = MessageFilter
    pagination_class = MessagePagination

    def get_queryset(self):
        """
        Return only messages from conversations
        where the current user is a participant.
        """
        user = self.request.user
        user_conversations = Conversation.objects.filter(users=user)
        return Message.objects.filter(
            conversation__in=user_conversations
        ).select_related('sender', 'conversation').order_by('-sent_at')

    def perform_create(self, serializer):
        """
        Automatically set the sender to the
        current user when creating a message.
        """
        serializer.save(sender=self.request.user)

    def perform_update(self, serializer):
        """
        Only allow message sender to update their own messages.
        """
        message = self.get_object()
        if message.sender != self.request.user:
            return Response(
                {'error': 'You can only update your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

    def perform_destroy(self, instance):
        """
        Only allow message sender to delete their own messages.
        """
        if instance.sender != self.request.user:
            return Response(
                {'error': 'You can only delete your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

    @action(detail=False, methods=['get'])
    def by_conversation(self, request):
        conversation_id = request.query_params.get('conversation_id')
        if not conversation_id:
            return Response(
                {'error': 'conversation_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(id=conversation_id)
            if request.user not in conversation.users.all():
                return Response(
                    {'error': 'You are not a participant in this conversation'},
                    status=status.HTTP_403_FORBIDDEN)

            messages = Message.objects.filter(
                conversation=conversation
            ).select_related('sender').order_by('sent_at')

            page = self.paginate_queryset(messages)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(messages, many=True)
            return Response(serializer.data)

        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def my_messages(self, request):
        messages = Message.objects.filter(
            sender=request.user
        ).select_related('conversation').order_by('-sent_at')

        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


@cache_page(60)  # Cache for 60 seconds
@login_required
def conversation_detail(request, username):
    other_user = get_object_or_404(User, username=username)

    # Fetch messages between the logged-in user and the other user
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).select_related('sender', 'receiver').order_by('timestamp')

    return render(request, 'messaging/conversation_detail.html', {
        'messages': messages,
        'other_user': other_user
    })
