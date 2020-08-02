from dataclasses import dataclass
from django.contrib.auth.models import User
from websockets.consumer import Consumer
from websockets.ws_methods import *


def chatroom_to_group(chatroom: str):
    return f"CHATROOM{chatroom}"


def send_message_to_chatroom(chatroom: str, sender: User, message: str):
    send_to_group(chatroom_to_group(chatroom), {
        "message": message,
        "sender": sender.username,
        "type": "group_message"
    })


def send_message_to_user(user, sender: User, message: str):
    send_to_user(user, {
        "message": message,
        "sender": sender.username,
        "type": "message"
    })


@dataclass
class ChatroomPayload:
    chatroom: str


@Consumer.ws_receiver("join_chatroom")
@payload_type(ChatroomPayload)
def join_chatroom(payload: ChatroomPayload, scope):
    user = scope["user"]
    group = chatroom_to_group(payload.chatroom)
    join_group(group, user)
    send_message_to_chatroom(payload.chatroom, user, "has joined chat")


@Consumer.ws_receiver("leave_chatroom")
@payload_type(ChatroomPayload)
def leave_chatroom(payload: ChatroomPayload, scope):
    user = scope["user"]
    leave_group(chatroom_to_group(payload.chatroom), user)


@dataclass
class ChatMessagePayload:
    receiver: int
    message: str


@Consumer.ws_receiver("chat_message")
@payload_type(ChatMessagePayload)
def handle_chat_message(payload: ChatMessagePayload, scope):
    sender = scope["user"]
    receiver = User.objects.get(pk=payload.receiver)
    send_message_to_user(receiver, sender, payload.message)


@dataclass
class ChatroomMessagePayload:
    chatroom: str
    message: str


@Consumer.ws_receiver("chatroom_message")
@payload_type(ChatroomMessagePayload)
def chatroom_message(payload: ChatroomMessagePayload, scope):
    sender = scope["user"]
    send_message_to_chatroom(payload.chatroom, sender, payload.message)
