from django.apps import AppConfig


class ChatAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat_app'

    def ready(self):
        # Import asyncio here if not already imported
        import asyncio
        # Import your consumer after Django apps are ready
        from .consumers import ChatConsumer

        # This ensures the async initialization runs only once when the app starts
        # and not on every consumer instance connection.
        # The 'if not ChatConsumer._initialized_globals' check inside _global_initialize
        # prevents re-initialization on development server reloads.
        print("Running ChatConsumer._global_initialize() from AppConfig.ready()")
        asyncio.run(ChatConsumer._global_initialize())