from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.test.utils import override_settings
from unittest.mock import patch
from .models import Message, Notification
from .signals import create_message_notification, create_welcome_notification


class MessageModelTest(TestCase):
    """Test cases for the Message model."""

    def setUp(self):
        """Set up test data."""
        self.sender = User.objects.create_user(
            username='sender', 
            email='sender@test.com',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver', 
            email='receiver@test.com',
            password='testpass123'
        )

    def test_message_creation(self):
        """Test that messages can be created properly."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message!"
        )

        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.receiver, self.receiver)
        self.assertEqual(message.content, "Hello, this is a test message!")
        self.assertFalse(message.is_read)
        self.assertIsNotNone(message.timestamp)

    def test_message_str_representation(self):
        """Test the string representation of Message."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="This is a test message that is longer than fifty characters to test truncation"
        )

        expected_str = f"From {self.sender.username} to {self.receiver.username}: This is a test message that is longer than fifty..."
        self.assertEqual(str(message), expected_str)

    def test_mark_as_read(self):
        """Test the mark_as_read method."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )

        self.assertFalse(message.is_read)
        message.mark_as_read()
        self.assertTrue(message.is_read)

    def test_message_ordering(self):
        """Test that messages are ordered by timestamp descending."""
        message1 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="First message"
        )
        message2 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Second message"
        )

        messages = Message.objects.all()
        self.assertEqual(messages[0], message2)  # Most recent first
        self.assertEqual(messages[1], message1)


class NotificationModelTest(TestCase):
    """Test cases for the Notification model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@test.com',
            password='testpass123'
        )
        self.sender = User.objects.create_user(
            username='sender', 
            email='sender@test.com',
            password='testpass123'
        )

    def test_notification_creation(self):
        """Test that notifications can be created properly."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.user,
            content="Test message"
        )

        notification = Notification.objects.create(
            user=self.user,
            message=message,
            notification_type='message',
            title='New message from sender',
            content='sender sent you a message: "Test message"'
        )

        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, 'message')
        self.assertFalse(notification.is_read)

    def test_create_message_notification_class_method(self):
        """Test the create_message_notification class method."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.user,
            content="Test message for notification"
        )

        notification = Notification.create_message_notification(message)

        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, 'message')
        self.assertEqual(notification.title, f'New message from {self.sender.username}')
        self.assertIn(self.sender.username, notification.content)
        self.assertIn('Test message for notification', notification.content)

    def test_mark_as_read(self):
        """Test the mark_as_read method."""
        notification = Notification.objects.create(
            user=self.user,
            notification_type='system',
            title='Test notification',
            content='This is a test notification'
        )

        self.assertFalse(notification.is_read)
        notification.mark_as_read()
        self.assertTrue(notification.is_read)


class MessageSignalTest(TestCase):
    """Test cases for message-related signals."""

    def setUp(self):
        """Set up test data."""
        self.sender = User.objects.create_user(
            username='sender', 
            email='sender@test.com',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver', 
            email='receiver@test.com',
            password='testpass123'
        )

    def test_notification_created_on_message_save(self):
        """Test that a notification is automatically created when a message is saved."""
        # Count notifications before
        initial_notification_count = Notification.objects.count()

        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="This should trigger a notification"
        )

        # Check that a notification was created
        self.assertEqual(Notification.objects.count(), initial_notification_count + 1)

        # Check the notification details
        notification = Notification.objects.latest('created_at')
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, 'message')
        self.assertIn(self.sender.username, notification.title)

    def test_no_notification_on_message_update(self):
        """Test that no new notification is created when a message is updated."""
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content"
        )

        # Count notifications after creation
        notification_count_after_creation = Notification.objects.count()

        # Update the message
        message.is_read = True
        message.save()

        # Check that no new notification was created
        self.assertEqual(Notification.objects.count(), notification_count_after_creation)

    def test_welcome_notification_created_on_user_creation(self):
        """Test that a welcome notification is created when a new user is created."""
        # Count notifications before
        initial_notification_count = Notification.objects.count()

        # Create a new user
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@test.com',
            password='testpass123'
        )

        # Check that a welcome notification was created
        self.assertEqual(Notification.objects.count(), initial_notification_count + 1)

        # Check the notification details
        notification = Notification.objects.latest('created_at')
        self.assertEqual(notification.user, new_user)
        self.assertEqual(notification.notification_type, 'system')
        self.assertIn('Welcome', notification.title)

    @patch('messaging.signals.logger')
    def test_signal_error_handling(self, mock_logger):
        """Test that signal errors are properly logged."""
        # Create a message with invalid data to trigger an error
        with patch('messaging.models.Notification.create_message_notification') as mock_create:
            mock_create.side_effect = Exception("Test error")

            Message.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                content="This should trigger an error"
            )

            # Check that the error was logged
            mock_logger.error.assert_called_once()


class SignalDisconnectionTest(TestCase):
    """Test cases for signal disconnection scenarios."""

    def setUp(self):
        """Set up test data."""
        self.sender = User.objects.create_user(
            username='sender', 
            email='sender@test.com',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver', 
            email='receiver@test.com',
            password='testpass123'
        )

    def test_signal_disconnection(self):
        """Test behavior when signals are disconnected."""
        # Disconnect the signal
        post_save.disconnect(create_message_notification, sender=Message)
        try:
            # Count notifications before
            initial_count = Notification.objects.count()

            # Create a message
            Message.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                content="This should not trigger a notification"
            )

            # Check that no notification was created
            self.assertEqual(Notification.objects.count(), initial_count)

        finally:
            # Reconnect the signal
            post_save.connect(create_message_notification, sender=Message)


class NotificationQueryTest(TestCase):
    """Test cases for notification queries and performance."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='user1', 
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2', 
            email='user2@test.com',
            password='testpass123'
        )

    def test_user_notifications_query(self):
        """Test querying notifications for a specific user."""
        # Create messages and notifications
        message1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="First message"
        )
        message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Second message"
        )

        # Get notifications for user1
        user1_notifications = Notification.objects.filter(user=self.user1)

        # Should have at least 2 notifications (from messages)
        self.assertGreaterEqual(user1_notifications.count(), 2)

        # All notifications should be for user1
        for notification in user1_notifications:
            self.assertEqual(notification.user, self.user1)

    def test_unread_notifications_count(self):
        """Test counting unread notifications."""
        # Create a message (which creates a notification)
        Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Unread message"
        )

        # Count unread notifications
        unread_count = Notification.objects.filter(
            user=self.user1,
            is_read=False
        ).count()

        self.assertGreater(unread_count, 0)

        # Mark one as read
        notification = Notification.objects.filter(user=self.user1).first()
        notification.mark_as_read()

        # Recount unread notifications
        new_unread_count = Notification.objects.filter(
            user=self.user1, 
            is_read=False
        ).count()

        self.assertEqual(new_unread_count, unread_count - 1)
