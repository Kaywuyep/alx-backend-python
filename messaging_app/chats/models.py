from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Additional fields:
    - phone_number: Optional phone number of the user.
    - bio: Optional short biography or description.
    - is_online: Boolean status to indicate if user is currently online.
    - last_seen: Timestamp of the user's last activity.
    """
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
    - users: Many-to-many relationship to User model
             representing conversation participants.
    - created_at: Timestamp when conversation was created.
    - updated_at: Timestamp when conversation was last updated.
    """
    users = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # pylint: disable=no-member
        usernames = ", ".join(user.username for user in self.users.all())
        return f"Conversation between: {usernames}"


class Message(models.Model):
    """
    Message model represents a single message sent in a conversation.

    Fields:
    - sender: Foreign key to User who sent the message.
    - conversation: Foreign key to the Conversation this message belongs to.
    - content: Text content of the message.
    - created_at: Timestamp when the message was created.
    - updated_at: Timestamp when the message was last updated.
    """
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='messages_sent')
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # pylint: disable=no-member
        return (
            f"Message from {self.sender.username} in Conversation {self.conversation.id}")
