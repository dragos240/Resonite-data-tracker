#!/usr/bin/env python3
from os import listdir
import os
import sys
from typing import List, Dict
import json
from datetime import date, datetime, timedelta

from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from util import (DataPoint,
                  hours_formatter,
                  month_formatter,
                  convert_dates,
                  convert_durations,
                  parse_out_data)


def time_per_day(data_points: List[DataPoint]):
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


def peak_play_times(data_points: List[DataPoint]):
    days_of_week = {"Sunday": [],
                    "Monday": [],
                    "Tuesday": [],
                    "Wednesday": [],
                    "Thursday": [],
                    "Friday": [],
                    "Saturday": []}

    for data_point in data_points:
        start: datetime = data_point.dt

        # Get hour as a float and day of week
        day_of_week = list(days_of_week.keys())[start.weekday()]
        hour = start.hour + start.minute / 60 + start.second / 3600

        days_of_week[day_of_week].append(hour)

    _, ax = plt.subplots()
    if not isinstance(ax, Axes):
        return

    boxplot_data: Dict = ax.boxplot(days_of_week.values(),
                                    labels=days_of_week.keys())
    if not isinstance(boxplot_data, Dict):
        return

    ax.yaxis.set_major_formatter(plt.FuncFormatter(hours_formatter))

    plt.gcf().autofmt_xdate()
    plt.xlabel("Day of week")
    plt.ylabel("Hour")
    plt.title("Resonite peak play times")

    plt.savefig("plots/peak-play-times.png")


def avg_daily_session_by_month(data_points: List[DataPoint]):
    def get_months(dates: List[date]) -> Dict[int, Dict[str, float]]:
        months = {}
        for d in dates:
            month = d.month
            if month not in months:
                months[month] = {"duration": 0, "days": 0}

        return months

    dates = convert_dates(data_points)
    durations = convert_durations(data_points)

    # Separate by month
    months = get_months(dates)
    avg_hours_per_day_by_month: Dict[int, float] = {}
    for d, duration in zip(dates, durations):
        for month in months.keys():
            if d.month == month:
                months[month]["duration"] += duration.total_seconds()
                months[month]["days"] += 1

    for month, data in months.items():
        avg_hours_per_day = data["duration"] // data["days"] / 3600
        avg_hours_per_day_by_month[month] = avg_hours_per_day

    _, ax = plt.subplots()
    if not isinstance(ax, Axes):
        return
    ax.bar(avg_hours_per_day_by_month.keys(),
           avg_hours_per_day_by_month.values())

    ax.xaxis.set_major_formatter(plt.FuncFormatter(month_formatter))

    ax.yaxis.set_major_formatter(plt.FuncFormatter(hours_formatter))

    plt.gcf().autofmt_xdate()
    plt.xticks(list(avg_hours_per_day_by_month.keys()))
    plt.ylabel("Duration (hours)")
    plt.xlabel("Month")
    plt.title("Average Resonite session per day by month")

    plt.savefig("plots/avg-time-per-day-by-month.png")


def time_by_week_day(data_points: List[DataPoint]):
    days_of_week = ["Sunday", "Monday", "Tuesday",
                    "Wednesday", "Thursday", "Friday",
                    "Saturday"]
    weekday_durations: Dict[str, List[timedelta]] \
        = {day_of_week: []
           for day_of_week in days_of_week}

    for data_point in data_points:
        dt = data_point.dt
        duration = data_point.duration
        day_of_week = days_of_week[dt.weekday()]

        weekday_durations[day_of_week].append(duration)

    weekday_averages = {}
    for day_of_week, durations in weekday_durations.items():
        total_days = len(durations)
        total_duration = timedelta(seconds=0)
        for duration in durations:
            total_duration += duration
        weekday_averages[day_of_week] = \
            (total_duration.total_seconds() / 3600) / total_days

    _, ax = plt.subplots()
    if not isinstance(ax, Axes):
        return
    ax.bar(days_of_week, weekday_averages.values())

    ax.yaxis.set_major_formatter(plt.FuncFormatter(hours_formatter))

    plt.gcf().autofmt_xdate()
    plt.ylabel("Duration (hours)")
    plt.xlabel("Day of week")
    plt.title("Average Resonite session by week day")

    plt.savefig("plots/time-by-week-day.png")


def time_per_week_number(data_points: List[DataPoint]):
    weeks: Dict[int, float] = {}
    for data_point in data_points:
        dt: datetime = data_point.dt
        duration = data_point.duration.total_seconds()
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
    parsed_data: List[DataPoint] = parse_out_data(documents)

    if not os.path.exists("plots"):
        os.mkdir("plots")

    time_per_day(parsed_data)
    avg_daily_session_by_month(parsed_data)
    time_by_week_day(parsed_data)
    time_per_week_number(parsed_data)
    peak_play_times(parsed_data)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Assuming all files in data")
        main([])
    elif len(sys.argv) >= 2:
        main(sys.argv[1:])
