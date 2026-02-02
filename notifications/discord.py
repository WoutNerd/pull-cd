import logging
import requests

from .base import Notifier


class DiscordNotifier(Notifier):
    def __init__(self, webhook_url: str, min_level: int):
        super().__init__(min_level)
        self.webhook_url = webhook_url

    def send(self, level: int, message: str):
        requests.post(
            self.webhook_url,
            json={
                "content": f"**{logging.getLevelName(level)}**\n{message}"
            },
            timeout=5,
        )
