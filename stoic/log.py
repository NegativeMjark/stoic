import logging
import datetime

class Iso8601Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        record_time = datetime.datetime.utcfromtimestamp(record.created)
        return record_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def console_config(level=logging.INFO):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(Iso8601Formatter(
        fmt="%(asctime)s|%(levelname)-7s|%(name)s|%(message)s",
    ))
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
