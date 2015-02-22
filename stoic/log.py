import logging
import logging.handlers
import datetime

DEFAULT_FORMAT = "%(asctime)s|%(levelname)-7s|%(name)s|%(message)s"

class Iso8601Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        record_time = datetime.datetime.utcfromtimestamp(record.created)
        return record_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def console_handler(level=logging.INFO, logger=logging.getLogger()):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(Iso8601Formatter(fmt=DEFAULT_FORMAT))
    logger.setLevel(level)
    logger.addHandler(handler)


def rotating_file_handler(filename, level=logging.INFO,
                          logger=logging.getLogger(), **kargs):
    handler = logging.handlers.TimedRotatingFileHandler(
        filename, utc=True, **kargs
    )
    handler.setLevel(level)
    handler.setFormatter(Iso8601Formatter(fmt=DEFAULT_FORMAT))
    logger.setLevel(level)
    logger.addHandler(handler)
