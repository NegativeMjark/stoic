import logging
import datetime

class Iso8601Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        record_time = datetime.datetime.utcfromtimestamp(record.created)
        return record_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
