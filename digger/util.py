from typing import Any, List, Dict
from datetime import date, datetime, timedelta
import calendar


def hours_formatter(hours_str, _) -> str:
    hours = int(hours_str)
    mins = int((hours_str - hours) * 60)

    return f"{hours}:{mins:02d}"


def month_formatter(month: int, _) -> str:
    if type(month) is not int:
        month = int(month)
    return calendar.month_name[month]


def convert_dates(data_points: List[Dict[str, Any]]) -> List[date]:
    dates = [data_point["date"]
             for data_point in data_points]
    return [datetime.strptime(date, "%Y-%m-%d")
            .date() for date in dates]


def convert_durations(data_points: List[Dict[str, Any]]) -> List[timedelta]:
    durations = [data_point["duration"]
                 for data_point in data_points]
    return [timedelta(seconds=int(s)) for s in durations]


def parse_out_data(documents: List[Dict]) -> List[Dict[str, str]]:
    def ts_to_datetime(ts: int):
        return datetime.fromtimestamp(ts)

    def ts_to_date(ts: int) -> str:
        dt = datetime.fromtimestamp(ts)
        date = dt.strftime("%Y-%m-%d")
        return date

    def gather_unique(data_points: List[Dict[str, str]]):
        unique_data_points: List[Dict[str, str]] = []
        last = None
        for data_point in sorted(data_points, key=lambda d: d["date"]):
            if (last is not None
                    and data_point["date"] == last["date"]
                    and data_point["duration"] == last["duration"]):
                continue
            unique_data_points.append(data_point)
            last = data_point

        return unique_data_points

    def combine_durations_for_date(data_points: List[Dict[str, str]]) \
            -> List[Dict[str, str]]:
        combined_data_points = []
        last = None
        for data_point in data_points:
            if (last is not None
                    and data_point["date"] == last["date"]):
                combined_data_points[-1]["duration"] += data_point["duration"]
            else:
                combined_data_points.append(data_point)
            last = data_point

        return combined_data_points

    data_points = []
    for document in documents:
        if document["identifier"] != "Resonite":
            continue
        _start_time = document["startTime"]
        date = ts_to_date(_start_time)
        dt = ts_to_datetime(_start_time)
        _duration = document["duration"]
        data_points.append({"date": date,
                            "datetime": dt,
                            "duration": _duration})

    unique_data_points = gather_unique(data_points)
    combined_data_points = combine_durations_for_date(unique_data_points)

    return combined_data_points
