import logging
from datetime import datetime
import pytz


class CustomFormatter(logging.Formatter):

    def __init__(self, fmt=None, datefmt=None, tz_name="Europe/Istanbul"):
        super().__init__(fmt, datefmt)
        self.tz = pytz.timezone(tz_name)

    def formatTime(self, record, datefmt=None):
        record_time = datetime.fromtimestamp(record.created, self.tz)
        return record_time.strftime(datefmt or "%Y-%m-%d %H:%M:%S")
