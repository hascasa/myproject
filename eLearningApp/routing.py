from django.urls import re_path
from . import consumers

# Define WebSocket URL patterns
websocket_urlpatterns = [
    # Route for the chat consumer, capturing the room name from the URL
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    
    # Route for the notification consumer
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
