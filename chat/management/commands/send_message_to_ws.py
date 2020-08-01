from django.core.management.base import BaseCommand

from websockets.ws_router import send_to_group


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_to_group("group", "YO WS, I AM A COMMAND")
