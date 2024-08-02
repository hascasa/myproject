import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

# Notification Consumer for enrolled students and teachers
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):  
        # Create a unique group name for the user based on their username
        self.user_group_name = f'notifications_{self.scope["user"].username}'

        # Add this WebSocket connection to the group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove this WebSocket connection from the group when disconnected
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def user_notification(self, event):
        # Handle the user notification event and send the notification to the WebSocket client
        notification_type = event.get('notification_type', 'generic')
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message,
            'notification_type': notification_type
        }))

# Chat consumer for the room chat in each course
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Retrieve the room name from the URL route parameters
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Add this WebSocket connection to the chat room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Accept the WebSocket connection
        await self.accept()

        # Notify the chat room that a new user has joined
        username = self.scope['user'].username 
        join_message = f"{username} has joined the chat room."
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': join_message
            }
        )

    async def disconnect(self, close_code):
        # Remove this WebSocket connection from the chat room group when disconnected
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive a message from the WebSocket client
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username

        # Format the message with a timestamp and the username
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"{username}: {message} ({timestamp})"

        # Send the formatted message to the chat room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': formatted_message
            }
        )

    async def chat_message(self, event):
        # Handle the chat message event and send the message to the WebSocket client
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
