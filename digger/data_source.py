from datetime import datetime, timedelta, date
import json
import os
from typing import List, Dict

import requests


class DataPoint:
    _dt: datetime
    _duration: timedelta
    game_name: str

    def __init__(self,
                 start: float,
                 duration: float,
                 game_name: str):
        self._dt = self.to_datetime(start)
        self._duration = self.to_timedelta(duration)
        self.game_name = game_name

    @staticmethod
    def to_datetime(ts: float) -> datetime:
        return datetime.fromtimestamp(ts)

    @staticmethod
    def to_timedelta(duration: float) -> timedelta:
        return timedelta(seconds=duration)

    def add_time(self, duration: timedelta):
        self._duration += duration

    @property
    def dt(self) -> datetime:
        return self._dt

    @dt.setter
    def dt(self, ts: float):
        self._dt = self.to_datetime(ts)

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, duration: float):
        self._duration = self.to_timedelta(duration)

    @property
    def date(self) -> date:
        return self._dt.date()

    def to_dict(self) -> Dict:
        dt = self.dt.timestamp()
        duration = self.duration.total_seconds()

        return {
            "dt": dt,
            "duration": duration,
            "game_name": self.game_name,
        }


class DataSource:
    """Abstract base class for data sources"""
    DATA_DIR = "./data_points"
    stored_data: List[DataPoint] = []

    @staticmethod
    def get_date_from_timestamp(timestamp: int) -> str:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

    def fetch(self) -> List[DataPoint]:
        """Fetch data from the source and return a list of data points"""
        return []

    @staticmethod
    def ensure_data_dir() -> str:
        """Ensure the data directory exists"""
        os.makedirs(DataSource.DATA_DIR, exist_ok=True)

        return DataSource.DATA_DIR

    def save(self):
        """
        Should either fetch the data with `fetch` or load the data
        saved with `fetch_and_store`
        """
        self.ensure_data_dir()

    def fetch_and_store(self):
        self.stored_data = self.fetch()

    @classmethod
    def from_json(cls, path: str) -> "DataSource":
        data_source = cls()
        with open(path, "r") as f:
            data = json.load(f)
            for data_point in data:
                dt: float = data_point["dt"]
                duration: float = data_point["duration"]
                game_name: str = data_point["game_name"]
                data_source.stored_data.append(
                    DataPoint(dt, duration, game_name))

        return data_source


class YurDataSource(DataSource):
    """Data source for YUR data"""
    YUR_API_URL = "https://yurapp-502de.firebaseapp.com/api/v2"
    YUR_URL = f"{YUR_API_URL}/secure/workout/get"

    def __init__(self,
                 token: str,
                 from_time: int,
                 to_time: int,
                 limit: int = 10000):
        self.from_time = from_time
        self.to_time = to_time
        self.headers = {"Authorization": f"Bearer {token}"}
        self.params = {
            "fromTime": self.from_time,
            "toTime": self.to_time,
            "limit": limit,
        }

    def fetch(self) -> List[DataPoint]:
        req = requests.get(self.YUR_URL,
                           headers=self.headers,
                           params=self.params)

        req.raise_for_status()

        json_data = req.json()

        data_points = []
        for document in json_data["documents"]:
            doc_start_time = int(document["startTime"])
            doc_duration = int(document["duration"])
            game_name: str = document["identifier"]
            data_points.append(
                DataPoint(doc_start_time, doc_duration, game_name))

        return data_points

    def save(self):
        super().save()

        from_date = self.get_date_from_timestamp(self.from_time)
        to_date = self.get_date_from_timestamp(self.to_time)

        savable_points = []
        for data_point in self.fetch():
            savable_points.append(data_point.to_dict())

        with open(f"{self.DATA_DIR}/yur-{from_date}-to-{to_date}.json",
                  "w") as f:
            f.write(json.dumps(savable_points))
