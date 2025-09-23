"""
ASGI config for dating_kit project.
"""

import os
from django.core.asgi import get_asgi_application

# 1️⃣ Set the settings module first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dating_kit.settings')

# 2️⃣ Load Django applications first
django_asgi_app = get_asgi_application()

# 3️⃣ Import Channels and your middleware/routing AFTER apps are loaded
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.middleware import JWTAuthMiddleware

import chat.routing

# 4️⃣ Define the ASGI application
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # HTTP requests handled by Django ASGI app
    "websocket": JWTAuthMiddleware(  # WebSocket requests go through your JWT middleware
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
