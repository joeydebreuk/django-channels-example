import random
from asgiref.sync import async_to_sync
from channels.auth import AuthMiddlewareStack
from channels.layers import get_channel_layer
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf.urls import url
import json


class ChatConsumer(AsyncJsonWebsocketConsumer):
    GROUP_NAME = "hardcodedgroup"

    async def connect(self):
        self.user = str(random.choice(["Jan", "Kees", "Willem", "Jaap"]))
        print("connect " + str(self.user))
        self.room_group_name = self.GROUP_NAME

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print("disconnect")
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive_json(self, data, **kwargs):
        print("receive: ", data["message"], kwargs)
        message = str(self.user) + ": " + data["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        print("process received: " + message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))


channel_layer = get_channel_layer()


def send_message_to_ws(message: str):
    async_to_sync(channel_layer.group_send)(ChatConsumer.GROUP_NAME, {
        "type": "chat_message",
        "message": message,
    })


urls = [
    url(r"^chat/$", ChatConsumer),
]

router = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(urls)
    ),
})
