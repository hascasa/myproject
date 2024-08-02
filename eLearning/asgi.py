

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import eLearningApp.routing

#  settings module for the 'django' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eLearning.settings')

# the ASGI application to handle different types of connections.
application = ProtocolTypeRouter({
    # HTTP protocol uses Django's ASGI application.
    "http": get_asgi_application(),
    
    # WebSocket protocol is handled by Channels
    "websocket": AuthMiddlewareStack(
        URLRouter(
            eLearningApp.routing.websocket_urlpatterns
        )
    ),
})
