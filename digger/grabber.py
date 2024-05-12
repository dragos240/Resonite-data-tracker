#!/usr/bin/env python3.9
import os
from argparse import ArgumentParser, Namespace
from datetime import datetime
import sys

from dotenv import load_dotenv
import requests

from digger.data_source import YurDataSource

load_dotenv()


def main(args: Namespace) -> int:
    if args.data_source == "yur":
        token = os.environ["yur_token"]
        start_ts = int(datetime.strptime(args.start, "%Y-%m-%d")
                       .timestamp())
        end_ts = int(datetime.strptime(args.end, "%Y-%m-%d")
                     .timestamp())
        yur_data_source = YurDataSource(token, start_ts, end_ts)

        try:
            yur_data_source.fetch_and_store()
        except requests.HTTPError:
            print("Authentication error")
            return -1

        yur_data_source.save()
    else:
        print(f"Selected data source {args.data_source} is not supported!")
        return 1

    return 0


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument(
        "start",
        type=str,
        help="The start date in YYYY-MM-SS")
    parser.add_argument(
        "end",
        type=str,
        help="The end date in YYYY-MM-SS")
    parser.add_argument("-d", "--data-source",
                        type=str,
                        choices=("yur",),
                        default="yur",
                        help="Data source to use")

    sys.exit(main(parser.parse_args()))
