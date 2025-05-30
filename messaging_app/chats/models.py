import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
# pylint: disable=no-member


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    
    Built-in fields from AbstractUser include:
    - email: Email address field
    - password: Password field (hashed)
    - first_name: First name field
    - last_name: Last name field
    - Primary key (id) is automatically created
    
    Additional fields:
    - user_id: UUID field as alternative identifier
    - phone_number: Optional phone number of the user.
    - bio: Optional short biography or description.
    - is_online: Boolean status to indicate if user is currently online.
    - last_seen: Timestamp of the user's last activity.
    """
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.username)


class Conversation(models.Model):
    """
    Conversation model represents a chat between multiple users.

    Fields:
    - conversation_id: UUID field as unique identifier
    - users: Many-to-many relationship to User model
             representing conversation participants.
    - created_at: Timestamp when conversation was created.
    - updated_at: Timestamp when conversation was last updated.
    """
    conversation_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    users = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        usernames = ", ".join(user.username for user in self.users.all())
        return f"Conversation between: {usernames}"


class Message(models.Model):
    """
    Message model represents a single message sent in a conversation.

    Fields:
    - message_id: UUID field as unique identifier
    - sender: Foreign key to User who sent the message.
    - conversation: Foreign key to the Conversation this message belongs to.
    - message_body: Text content of the message.
    - sent_at: Timestamp when the message was sent.
    - updated_at: Timestamp when the message was last updated.
    """
    message_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='messages_sent')
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Message from {self.sender.username} in Conversation {self.conversation.id}")