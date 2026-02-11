import logging
import queue

class GuiLoggerHandler(logging.Handler):
    """
    A custom logging handler that sends log records to a queue.
    This allows the GUI to consume log messages in a thread-safe manner.
    """
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_queue.put({
                "level": record.levelname,
                "message": msg,
                "timestamp": record.created
            })
        except Exception:
            self.handleError(record)
