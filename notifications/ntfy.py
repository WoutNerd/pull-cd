import logging
import requests

from .base import Notifier


class NtfyNotifier(Notifier):
    def __init__(self, topic_url: str, min_level: int):
        super().__init__(min_level)
        self.topic_url = topic_url

    def send(self, level: int, message: str):
        requests.post(
            self.topic_url,
            data=message.encode(),
            headers={
                "Title": logging.getLevelName(level),
                "Priority": "5" if level >= logging.ERROR else "3",
            },
            timeout=5,
        )
