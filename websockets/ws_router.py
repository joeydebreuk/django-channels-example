from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from websockets.consumer import Consumer

router = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([url("", Consumer)])
    ),
})
