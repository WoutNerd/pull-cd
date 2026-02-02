import logging
import requests

from .base import Notifier


class GotifyNotifier(Notifier):
    def __init__(self, url: str, token: str, min_level: int):
        super().__init__(min_level)
        self.url = url.rstrip("/")
        self.token = token

    def send(self, level: int, message: str):
        requests.post(
            f"{self.url}/message",
            headers={"X-Gotify-Key": self.token},
            json={
                "title": logging.getLevelName(level),
                "message": message,
                "priority": 5 if level >= logging.ERROR else 3,
            },
            timeout=5,
        )
