import time
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Message, Notification
# Custom signal for bulk message operations
from django.dispatch import Signal
from .models import MessageHistory

# Define custom signal
bulk_messages_created = Signal()

# Get the user model
User = get_user_model()


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal handler that creates a notification when a new message is created.

    Args:
        sender: The model class (Message)
        instance: The actual Message instance
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        try:
            # Create notification for the receiver
            Notification.create_message_notification(instance)

            print(
                f"Notification created for user {instance.receiver.username} "
                f"about message from {instance.sender.username}"
            )

            # You can add additional logic here, such as:
            # - Sending email notifications
            # - Pushing real-time notifications via WebSocket
            # - Sending push notifications to mobile devices

        except ValueError as e:
            print(f"Failed to create notification for message {instance.id}: {str(e)}")


@receiver(post_save, sender=User)
def create_welcome_notification(sender, instance, created, **kwargs):
    """
    Signal handler that creates a welcome notification for new users.

    Args:
        sender: The model class (User)
        instance: The actual User instance
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        try:
            Notification.objects.create(
                user=instance,
                notification_type='system',
                title='Welcome to the Messaging System!',
                content=f'Hi {instance.username}! Welcome to our messaging platform. '
                       'You can now send and receive messages from other users.'
            )

            print(f"Welcome notification created for new user {instance.username}")

        except Exception as e:
            print(f"Failed to create welcome notification for user {instance.id}: {str(e)}")


@receiver(post_delete, sender=Message)
def cleanup_message_notifications(sender, instance, **kwargs):
    """
    Signal handler that cleans up notifications when a message is deleted.

    Args:
        sender: The model class (Message)
        instance: The actual Message instance
        **kwargs: Additional keyword arguments
    """
    try:
        # Delete related notifications
        deleted_count = Notification.objects.filter(message=instance).delete()[0]

        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} notifications for deleted message {instance.id}")

    except Exception as e:
        print(f"Failed to cleanup notifications for deleted message {instance.id}: {str(e)}")


@receiver(bulk_messages_created)
def handle_bulk_message_notifications(sender, messages, **kwargs):
    """
    Signal handler for bulk message creation.
    
    Args:
        sender: The sender of the signal
        messages: List of Message instances
        **kwargs: Additional keyword arguments
    """
    try:
        notifications = []
        for message in messages:
            notification = Notification(
                user=message.receiver,
                message=message,
                notification_type='message',
                title=f'New message from {message.sender.username}',
                content=f'{message.sender.username} sent you a message: "{message.content[:100]}..."'
            )
            notifications.append(notification)

        # Bulk create notifications for efficiency
        Notification.objects.bulk_create(notifications)

        print(f"Bulk created {len(notifications)} notifications for {len(messages)} messages")

    except Exception as e:
        print(f"Failed to bulk create notifications: {str(e)}")


# Signal for notification read status changes
@receiver(post_save, sender=Notification)
def log_notification_read_status(sender, instance, created, **kwargs):
    """
    Signal handler that logs when notifications are read.

    Args:
        sender: The model class (Notification)
        instance: The actual Notification instance
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if not created and instance.is_read:
        print(
            f"Notification {instance.id} marked as read by user {instance.user.username}"
        )


@receiver(pre_save, sender=Message)
def track_message_edit(sender, instance, **kwargs):
    """
    Before saving a Message, check if the content has changed.
    If yes, save the old content in MessageHistory.
    """
    if not instance.pk:
        return  # New message, skip

    try:
        old_message = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return  # Shouldn't happen, but guard anyway

    if old_message.content != instance.content:
        # Save to MessageHistory
        MessageHistory.objects.create(
            message=instance,
            old_content=old_message.content
        )
        # Mark as edited
        instance.edited = True
        instance.edited_at = time.time()
