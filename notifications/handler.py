import logging


class NotificationHandler(logging.Handler):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    def emit(self, record: logging.LogRecord):
        try:
            message = self.format(record)
            self.manager.notify(record.levelno, message)
        except Exception:
            # Never let notification errors break logging
            self.handleError(record)
