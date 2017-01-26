#! -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from settings import DATE_FORMAT, DATETIME_FORMAT

ONE_DAY = timedelta(days=1)
ONE_MINUTE = timedelta(minutes=1)

class ShopwaveDatetime(datetime):
    def __new__(cls, d=None):
        """
        d : string or datetime.datetime instance
        """
        if d is None:
            d = datetime.now()
        if not (hasattr(d,'year') and hasattr(d,'month') and hasattr(d,'day')):
            d = d.strip()
            if len(d) == 10: 
                d += ' 00:00:00'
            elif len(d) > 19:
                d = d[:19]
            try:
                d = datetime.strptime(d,  '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                d = datetime.strptime(d, DATETIME_FORMAT)
            except ValueError as e:
                raise e

        day = d.day
        month = d.month
        year = d.year
        hour = getattr(d, 'hour', 0)
        minute = getattr(d, 'minute', 0)
        second = getattr(d, 'second', 0)

        return datetime.__new__(cls, year, month, day, hour, minute, second)


    def to_str(self):
        return datetime.strftime(self, DATETIME_FORMAT)

    @classmethod
    def now(cls):
        return cls()

    def __str__(self):
        return self.to_str()

            






