"""
ASGI config for chat_agent_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

# --- IMPORTANT: These lines must come BEFORE any imports that load Django apps/models ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_agent_project.settings')
django.setup()
# --- End of critical setup ---

# Now you can import your application-specific routing and other Django-dependent modules
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat_app.routing import websocket_urlpatterns # <--- Moved this line here
# ---------------------------------------------------------------------------------------


application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    'websocket':AuthMiddlewareStack(     # Wrap your WebSocket routing
        URLRouter(websocket_urlpatterns)
    ),
})