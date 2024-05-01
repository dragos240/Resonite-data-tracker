#!/usr/bin/env python3
from os import listdir
import os
import sys
from typing import Any, List, Dict, Tuple
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


def hours_formatter(hours_str, _) -> str:
    hours = int(hours_str)
    mins = int((hours_str - hours) * 60)

    return f"{hours}:{mins:02d}"


def convert_durations(data_points: List[Dict[str, Any]]) -> List[timedelta]:
    durations = [data_point["duration"]
                 for data_point in data_points]
    return [timedelta(seconds=int(s)) for s in durations]


def time_per_day(data_points: List[Dict[str, Any]]):
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


def time_by_week_day(data_points: List[Dict[str, Any]]):
    days_of_week = ["Sunday", "Monday", "Tuesday",
                    "Wednesday", "Thursday", "Friday",
                    "Saturday"]
    weekday_durations = {day_of_week: []
                         for day_of_week in days_of_week}

    for data_point in data_points:
        dt = data_point["datetime"]
        duration = data_point["duration"]
        day_of_week = days_of_week[dt.weekday()]

        weekday_durations[day_of_week].append(duration)

    weekday_averages = {}
    for day_of_week, durations in weekday_durations.items():
        total_days = len(durations)
        total_duration = 0
        for duration in durations:
            total_duration += duration
        weekday_averages[day_of_week] = (total_duration / 3600) / total_days

    _, ax = plt.subplots()
    if not isinstance(ax, Axes):
        return
    ax.bar(days_of_week, weekday_averages.values())

    # ax.yaxis.set_major_locator(plt.MaxNLocator())
    ax.yaxis.set_major_formatter(plt.FuncFormatter(hours_formatter))

    plt.gcf().autofmt_xdate()
    plt.ylabel("Duration (hours)")
    plt.xlabel("Day of week")
    plt.title("Average Resonite session by week day")

    plt.savefig("plots/time-by-week-day.png")


def time_per_week_number(data_points: List[Dict[str, Any]]):
    weeks: Dict[int, float] = {}
    for data_point in data_points:
        dt: datetime = data_point["datetime"]
        duration: int = data_point["duration"]
        week_num = int(dt.strftime("%U"))
        if week_num not in weeks:
            weeks[week_num] = 0
        weeks[week_num] += duration

    # Convert seconds to hours
    weeks = {week_num: duration / 3600
             for week_num, duration in weeks.items()}

    _, ax = plt.subplots()
    if not isinstance(ax, Axes):
        return
    ax.bar(weeks.keys(), weeks.values())

    ax.yaxis.set_major_formatter(plt.FuncFormatter(hours_formatter))

    plt.gcf().autofmt_xdate()
    plt.ylabel("Duration per week (hours)")
    plt.xlabel("Week")
    plt.title("Time spent per week")

    plt.savefig("plots/time-by-week-number.png")


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


def main(json_files: List[str]):
    documents: List[Dict] = []
    if not json_files:
        for path in listdir("data"):
            if not path.endswith(".json"):
                continue
            json_files.append(f"data/{path}")
    for file in json_files:
        print("Processing", file)
        with open(file, 'r') as f:
            documents.extend(json.loads(f.read())["documents"])
    parsed_data: List[Dict[str, str]] = parse_out_data(documents)

    if not os.path.exists("plots"):
        os.mkdir("plots")

    time_per_day(parsed_data)
    time_by_week_day(parsed_data)
    time_per_week_number(parsed_data)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Assuming all files in data")
        main([])
    elif len(sys.argv) >= 2:
        main(sys.argv[1:])
