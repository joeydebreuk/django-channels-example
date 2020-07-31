import random
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf.urls import url
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = str(random.choice(["Jan", "Kees", "Willem", "Jaap"]))
        print("connect " + str(self.user))
        self.room_name = "testgroup"  # hardcoded for now
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print("disconnect")
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        print("receive: " + text_data)
        text_data_json = json.loads(text_data)
        message = str(self.user) + ": " + text_data_json["message"]

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


urls = [
    url(r"^chat/$", ChatConsumer),
]

router = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(urls)
    ),
})
