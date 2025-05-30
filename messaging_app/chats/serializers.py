from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone_number', 'bio',
            'is_online', 'last_seen',
        ]


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.
    Includes sender info as nested UserSerializer.
    """
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'content', 'created_at', 'updated_at',
        ]


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model.
    Includes nested participants and messages.
    """
    users = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id', 'users', 'messages', 'created_at', 'updated_at',
        ]
