from copy import copy
from functools import wraps

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Move this to redis
user_channel_store = dict()


def create_message(payload: [object, list]):
    return dict(
        payload=payload,
        type="handle_send"
    )


def get_user_group(user):
    return f"USER{user.pk}"


def send(group: str, payload: object):
    async_to_sync(get_channel_layer().group_send)(group, create_message(payload))


def send_to_user(user, payload: object):
    send(get_user_group(user), payload)


def join_group(group: str, user):
    channel = user_channel_store[user.id]
    async_to_sync(get_channel_layer().group_add)(group, channel)


def leave_group(group: str, user):
    channel = user_channel_store[user.id]
    async_to_sync(get_channel_layer().group_discard)(group, channel)


def payload_type(payload_constructor):
    def decorator(fn):
        @wraps(fn)
        def wrapper(payload, *args, **kwargs):
            print("payload = ", payload)
            payload_copy = copy(payload)
            del payload_copy["type"]
            return fn(payload_constructor(**payload_copy), *args, **kwargs)
        return wrapper
    return decorator
