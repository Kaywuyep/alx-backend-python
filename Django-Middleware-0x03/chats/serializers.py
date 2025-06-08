from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    # Using CharField for additional validation or custom fields
    username = serializers.CharField(max_length=150)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_id', 'phone_number', 'bio', 'is_online', 'last_seen',
        ]
    
    def validate_username(self, value):
        """
        Custom validation for username field.
        """
        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must be at least 3 characters long.")
        return value


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.
    Includes sender info as nested UserSerializer.
    """
    sender = UserSerializer(read_only=True)
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'message_id', 'sender', 'sender_name', 'message_body',
            'sent_at', 'updated_at',
        ]
    
    def get_sender_name(self, obj):
        """
        Method field to get sender's display name.
        """
        return (
            f"{obj.sender.first_name} {obj.sender.last_name}".strip() or obj.sender.username)


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model.
    Includes nested participants and messages.
    """
    users = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'conversation_id', 'users', 'messages',
            'participant_count', 'created_at', 'updated_at',
        ]
    
    def get_participant_count(self, obj):
        """
        Method field to get the number of participants in the conversation.
        """
        return obj.users.count()
    
    def validate(self, attrs):
        """
        Custom validation for conversation data.
        """
        # Example validation - ensure conversation has participants
        if hasattr(self.instance, 'users') and self.instance.users.count() == 0:
            raise serializers.ValidationError(
                "Conversation must have at least one participant.")
        return attrs
