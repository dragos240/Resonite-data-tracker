#!/usr/bin/env python3.9
import os
from argparse import ArgumentParser, Namespace
from datetime import datetime
import json

from dotenv import load_dotenv
import requests

load_dotenv()


def main(args: Namespace):
    token = os.environ["yur_token"]
    api_url = "https://yurapp-502de.firebaseapp.com/api/v2"
    url = f"{api_url}/secure/workout/get"
    start_ts = int(datetime.strptime(args.startdate, "%Y-%m-%d").timestamp())
    end_ts = int(datetime.strptime(args.enddate, "%Y-%m-%d").timestamp())

    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "fromTime": start_ts,
        "toTime": end_ts,
        "limit": 100000}

    req = requests.get(url,
                       headers=headers,
                       params=params)

    try:
        req.raise_for_status()
    except requests.HTTPError:
        print("Authentication error")
        return

    with open(f"data/data-{args.startdate}-{args.enddate}.json", "w") as f:
        f.write(json.dumps(req.json(), indent=2))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "startdate",
        type=str,
        help="The start date in YYYY-MM-SS")
    parser.add_argument(
        "enddate",
        type=str,
        help="The end date in YYYY-MM-SS")
    main(parser.parse_args())
