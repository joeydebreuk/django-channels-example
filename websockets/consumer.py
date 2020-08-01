from functools import wraps
from threading import Thread
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from websockets.ws_methods import get_user_group, user_channel_store


class Consumer(AsyncJsonWebsocketConsumer):
    """
    Every receiver gets called on "receive_json"
    with the received data.

    Receivers can be added with "Consumer.ws_receiver",
    optionally specifying which type should be received like:

        @Consumer.ws_receiver("new_message")
        def receive_new_message(payload):
               # payload["type"] == "new_message"
               ...
    """
    receivers = []

    @classmethod
    def ws_receiver(cls, type_name: str = None):
        def decorator(fn):
            @wraps(fn)
            def wrapper(payload, *args, **kwargs):
                if not type_name or payload["type"] == type_name:
                    return fn(payload, *args, **kwargs)

            cls.receivers.append(wrapper)
            return wrapper

        return decorator

    async def connect(self):
        # If you are to lazy to login, uncomment:
        # from django.contrib.auth.models import User
        # self.scope["user"] = User.objects.first()

        user = self.scope["user"]
        print("connect " + str(user))
        user_channel_store[user.id] = self.channel_name
        await self.channel_layer.group_add(get_user_group(user), self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        print(f"disconnect {user}")
        await self.channel_layer.group_discard(get_user_group(user), self.channel_name)

    # Receive message from WebSocket
    async def receive_json(self, payload, **kwargs):
        Thread(target=self.run_receivers, args=[payload, self.scope]).start()

    def run_receivers(self, *args, **kwargs):
        for receiver in self.receivers:
            receiver(*args, **kwargs)

    async def handle_send(self, event):
        await self.send(text_data=json.dumps(event["payload"]))
