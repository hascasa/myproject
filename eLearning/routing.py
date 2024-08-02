

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import eLearningApp.routing

#the ASGI application to handle different types of connections.
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            eLearningApp.routing.websocket_urlpatterns
        )
    ),
})
