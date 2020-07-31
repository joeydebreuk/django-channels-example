from django.core.management.base import BaseCommand

from websockets.ws_router import send_message_to_ws


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_message_to_ws("YO WS, I AM A COMMAND")
