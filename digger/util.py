from typing import List, Dict
from datetime import datetime, timedelta, date
import calendar


class DataPoint:
    _dt: datetime
    _duration: timedelta

    def __init__(self, start: int, duration: int):
        self._dt = self.to_datetime(start)
        self._duration = self.to_timedelta(duration)

    @staticmethod
    def to_datetime(ts: int) -> datetime:
        return datetime.fromtimestamp(ts)

    @staticmethod
    def to_timedelta(duration: int) -> timedelta:
        return timedelta(seconds=duration)

    def add_time(self, duration: timedelta):
        self._duration += duration

    @property
    def dt(self) -> datetime:
        return self._dt

    @dt.setter
    def dt(self, ts: int):
        self._dt = self.to_datetime(ts)

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, duration: int):
        self._duration = self.to_timedelta(duration)

    @property
    def date(self) -> date:
        return self._dt.date()


def hours_formatter(hours_str, _) -> str:
    hours = int(hours_str)
    mins = int((hours_str - hours) * 60)

    return f"{hours}:{mins:02d}"


def month_formatter(month: int, _) -> str:
    if type(month) is not int:
        month = int(month)
    return calendar.month_name[month]


def convert_dates(data_points: List[DataPoint]) -> List[date]:
    dates = [data_point.date
             for data_point in data_points]
    return dates


def convert_durations(data_points: List[DataPoint]) -> List[timedelta]:
    durations = [data_point.duration
                 for data_point in data_points]
    return durations


def parse_out_data(documents: List[Dict]) -> List[DataPoint]:
    def gather_unique(data_points: List[DataPoint]):
        unique_data_points: List[DataPoint] = []
        last = None
        for data_point in sorted(data_points, key=lambda d: d.date):
            if (last is not None
                    and data_point.dt == last.dt
                    and data_point.duration == last.duration):
                continue
            unique_data_points.append(data_point)
            last = data_point

        return unique_data_points

    def combine_durations_for_date(data_points: List[DataPoint]) \
            -> List[DataPoint]:
        combined_data_points: List[DataPoint] = []
        last = None
        for data_point in data_points:
            if (last is not None
                    and data_point.dt == last.dt):
                combined_data_points[-1].add_time(data_point.duration)
            else:
                combined_data_points.append(data_point)
            last = data_point

        return combined_data_points

    data_points: List[DataPoint] = []
    for document in documents:
        if document["identifier"] != "Resonite":
            continue
        start_time = document["startTime"]
        duration = document["duration"]
        data_points.append(DataPoint(start_time, duration))

    unique_data_points = gather_unique(data_points)
    combined_data_points = combine_durations_for_date(unique_data_points)

    return combined_data_points
