#!/usr/bin/env python3.9

import json
import os
from datetime import datetime
from typing import Tuple

from digger.data_source import DataSource
from digger.util import DataPoint


def parse_dates(filename: str) -> Tuple[str, str]:
    number_split = filename.replace("data-", "") \
                           .replace(".json", "") \
                           .split("-")

    from_date = ""
    to_date = ""
    if len(number_split) == 2:
        # Must be a timestamp format
        for idx, num in enumerate(number_split):
            dt = datetime.fromtimestamp(int(num))
            date_formatted = dt.strftime("%Y-%m-%d")
            if idx == 0:
                from_date = date_formatted
            else:
                to_date = date_formatted

    elif len(number_split) == 6:
        # Must be a date format
        from_date = "-".join(number_split[:3])
        to_date = "-".join(number_split[3:])

    else:
        print(number_split, len(number_split))
        return from_date, to_date
        # raise Exception("Invalid format!")

    return from_date, to_date


def main():
    old_data_dir = "./data"
    data_dir = DataSource.ensure_data_dir()

    for filename in os.listdir(old_data_dir):
        if not filename.endswith(".json"):
            continue
        from_date, to_date = parse_dates(filename)
        path = os.path.join(old_data_dir, filename)

        savable_points = []
        with open(path, "r") as f:
            json_data = json.loads(f.read())
            for document in json_data["documents"]:
                start_time = document["startTime"]
                duration = document["duration"]
                game_name = document["identifier"]
                savable_points.append(
                    DataPoint(start_time, duration, game_name).to_dict())

        with open(f"{data_dir}/yur-{from_date}-to-{to_date}.json",
                  "w") as f:
            f.write(json.dumps(savable_points))


if __name__ == '__main__':
    main()
