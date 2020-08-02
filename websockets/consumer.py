from functools import wraps
from threading import Thread
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from websockets.ws_methods import user_channel_store


def get_dummy_user():
    from django.contrib.auth.models import User
    user = User.objects.first()
    if user:
        return user
    return User.objects.create(username="henkie")


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
        if not self.scope["user"].is_authenticated:
            self.scope["user"] = get_dummy_user()

        user = self.scope["user"]
        print("connect " + str(user))
        user_channel_store[user.id] = self.channel_name
        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        print(f"disconnect {user}")

    # Receive message from WebSocket
    async def receive_json(self, payload, **kwargs):
        Thread(target=self.run_receivers, args=[payload, self.scope]).start()

    def run_receivers(self, *args, **kwargs):
        for receiver in self.receivers:
            receiver(*args, **kwargs)

    async def handle_send(self, event):
        await self.send(text_data=json.dumps(event["payload"]))
