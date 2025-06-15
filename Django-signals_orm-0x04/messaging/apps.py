from django.apps import AppConfig


class MessagingConfig(AppConfig):
    """
    Configuration for the messaging app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'
    verbose_name = 'Messaging System'

    def ready(self):
        """
        Import signal handlers when the app is ready.
        This ensures that the signals are connected when Django starts.
        """
        try:
            # Import signals to ensure they are connected
            import messaging.signals
            # You can also perform other initialization tasks here
            print("Messaging app signals loaded successfully")

        except ImportError as e:
            print(f"Error importing messaging signals: {e}")
        except Exception as e:
            print(f"Error in messaging app ready(): {e}")
