from django.urls import re_path
from . import consumers

#  WebSocket URL patterns for chat and notifications
websocket_urlpatterns = [
    # URL pattern for chat functionality
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),

    # URL pattern for notifications
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]

# Assign websocket_urlpatterns to urlpatterns for use in routing
urlpatterns = websocket_urlpatterns
