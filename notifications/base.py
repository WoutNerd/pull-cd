import logging
from abc import ABC, abstractmethod


class Notifier(ABC):
    def __init__(self, min_level: int):
        self.min_level = min_level

    def should_notify(self, level: int) -> bool:
        return level >= self.min_level

    @abstractmethod
    def send(self, level: int, message: str):
        pass
