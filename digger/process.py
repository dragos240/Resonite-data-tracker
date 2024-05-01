import json
from typing import Dict
import csv
from datetime import datetime
import sys


def load_json(path: str) -> Dict:
    with open(path, 'r') as f:
        return json.loads(f.read())


def process(data: Dict):
    def seconds_to_duration(seconds: int):
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return f"{hours}:{minutes}:{seconds}"

    def ts_to_date(ts: int):
        dt = datetime.fromtimestamp(ts)
        date = dt.strftime("%Y-%m-%d")
        return date

    headers = "date,duration".split(",")
    documents = data["documents"]
    parsed_data = []
    duration = 0
    with open("results.csv", "w") as f:
        entry_writer = csv.DictWriter(f, fieldnames=headers)
        entry_writer.writeheader()
        for document in documents:
            if document["identifier"] != "Resonite":
                continue
            duration = document["duration"]
            start_time: int = document["startTime"]
            date = ts_to_date(start_time)
            if parsed_data and date == parsed_data[-1]["date"]:
                parsed_data[-1]["duration"] += duration
                continue
            parsed_data.append({"date": date,
                                "duration": duration})

        for entry in parsed_data:
            date = entry["date"]
            duration = seconds_to_duration(entry["duration"])
            entry_writer.writerow({"date": date,
                                   "duration": duration})


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Syntax {sys.argv[0]} FILE")
        sys.exit()
    data = load_json(sys.argv[1])
    process(data)
