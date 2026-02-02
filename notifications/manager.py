import logging

from .base import Notifier

_notify_logger = logging.getLogger("notifications")
_notify_logger.propagate = False 
_notify_logger.setLevel(logging.ERROR)


class NotificationManager:
    def __init__(self, notifiers):
        self.notifiers = notifiers

    def notify(self, level: int, message: str):
        for notifier in self.notifiers:
            if notifier.should_notify(level):
                try:
                    notifier.send(level, message)
                except Exception:
                    _notify_logger.exception(
                        "Notification failed for %s",
                        notifier.__class__.__name__,
                    )


