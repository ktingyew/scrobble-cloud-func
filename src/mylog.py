from datetime import datetime
import logging

from pytz import timezone

class myFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.converter = lambda *args: datetime.now(tz=timezone('Asia/Singapore')).timetuple()
