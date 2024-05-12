from typing import List
from datetime import timedelta, date
import calendar

from .data_source import DataPoint, DataSource


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


def extract_data_points(data_sources: List[DataSource],
                        game_name: str) -> List[DataPoint]:
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
    for data_source in data_sources:
        for data_point in data_source.stored_data:
            if data_point.game_name != game_name:
                continue
            data_points.append(data_point)

    unique_data_points = gather_unique(data_points)
    combined_data_points = combine_durations_for_date(unique_data_points)

    return combined_data_points
