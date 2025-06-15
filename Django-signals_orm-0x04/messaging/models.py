from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


class Message(models.Model):
    """
    Model representing a message between users.
    """
    sender = models.ForeignKey(
        # User,
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="User who sent the message"
    )
    receiver = models.ForeignKey(
        # User,
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='received_messages',
        help_text="User who will receive the message"
    )
    content = models.TextField(
        help_text="Content of the message"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When the message was created"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the message has been read by the receiver"
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return (
            f"From {self.sender.username} to {self.receiver.username}: {self.content[:50]}...")

    def mark_as_read(self):
        """Mark this message as read."""
        self.is_read = True
        self.save(update_fields=['is_read'])


class Notification(models.Model):
    """
    Model representing a notification for a user.
    """
    NOTIFICATION_TYPES = (
        ('message', 'New Message'),
        ('system', 'System Notification'),
        ('alert', 'Alert'),
    )

    user = models.ForeignKey(
        # User,
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="User who will receive the notification"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True,
        blank=True,
        help_text="Related message (if applicable)"
    )
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        help_text="The parent message this is replying to"
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='message',
        help_text="Type of notification"
    )
    title = models.CharField(
        max_length=200,
        help_text="Notification title"
    )
    edited = models.BooleanField(
        default=False,
        help_text="Message edited")
    edited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last edited")
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='edited_messages'
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Message Read"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the notification was created"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

    def mark_as_read(self):
        """Mark this notification as read."""
        self.is_read = True
        self.save(update_fields=['is_read'])

    def is_root_message(self):
        """root message
        """
        return self.parent_message is None

    def get_thread(self):
        """
        Recursively get all replies to this message.
        """
        replies = list(self.replies.all())
        for reply in replies:
            replies.extend(reply.get_thread())
        return replies

    @classmethod
    def create_message_notification(cls, message):
        """
        Class method to create a notification for a new message.
        """
        return cls.objects.create(
            user=message.receiver,
            message=message,
            notification_type='message',
            title=f'New message from {message.sender.username}',
            content=f'{message.sender.username} sent you a message: "{message.content[:100]}..."'
        )


class MessageHistory(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for message {self.message.id} at {self.edited_at}"
