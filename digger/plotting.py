#!/usr/bin/env python3
import sys
from typing import Any, List, Dict
import json
from datetime import date, datetime, timedelta

from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def convert_dates(data_points: List[Dict[str, Any]]) -> List[date]:
    dates = [data_point["date"]
             for data_point in data_points]
    return [datetime.strptime(date, "%Y-%m-%d")
            .date() for date in dates]


def convert_durations(data_points: List[Dict[str, Any]]) -> List[timedelta]:
    durations = [data_point["duration"]
                 for data_point in data_points]
    return [timedelta(seconds=int(s)) for s in durations]


def time_per_day(data_points: List[Dict[str, Any]]):
    def hours_formatter(hours_str, _) -> str:
        hours = int(hours_str)
        mins = int((hours_str - hours) * 60)

        return f"{hours}h{mins}m"

    dates = convert_dates(data_points)
    durations = convert_durations(data_points)

    duration_in_hours = [duration.total_seconds() / 3600
                         for duration in durations]

    _, ax = plt.subplots()
    if not isinstance(ax, Axes):
        return
    ax.scatter(dates, duration_in_hours)

    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

    ax.yaxis.set_major_locator(plt.MaxNLocator())
    ax.yaxis.set_major_formatter(plt.FuncFormatter(hours_formatter))

    plt.gcf().autofmt_xdate()
    plt.ylabel("Duration (hours)")
    plt.xlabel("Date")
    plt.title("Time spent per day")

    plt.savefig("plots/time-per-day.png")


def time_by_week(data_points: List[Dict[str, Any]]):
    dates = [data_point["date"] for data_point in data_points]
    durations = [data_point["duration"] for data_point in data_points]


def parse_out_data(documents: List[Dict]) -> List[Dict[str, str]]:
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
        date = ts_to_date(document["startTime"])
        duration = document["duration"]
        data_points.append({"date": date, "duration": duration})

    unique_data_points = gather_unique(data_points)
    combined_data_points = combine_durations_for_date(unique_data_points)

    return combined_data_points


def main(json_files: List[str]):
    documents: List[Dict] = []
    for file in json_files:
        with open(file, 'r') as f:
            documents.extend(json.loads(f.read())["documents"])
    parsed_data: List[Dict[str, str]] = parse_out_data(documents)
    time_per_day(parsed_data)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Must include one or more JSON path")
        sys.exit()
    elif len(sys.argv) == 2:
        main([sys.argv[1]])
    else:
        main(sys.argv[1:])
