#!/usr/bin/env python2

import argparse
import os.path
import sys

import rrdtool


RRDTOOL_SOURCES = [
    # Heartbeat of 900 means maximum of 15 minutes before UNKNOWN value.
    'DS:decawatts:COUNTER:900:0:U',
]
RRDTOOL_ARCHIVES = [
    # Three months (95 days) of every 15 minutes.
    'RRA:AVERAGE:0.5:3:9200',
    # Five years of hourly data.
    'RRA:AVERAGE:0.5:12:44000',
]


def create_database(database_path):
    if os.path.exists(database_path):
        return
    rrdtool.create(database_path, RRDTOOL_SOURCES, RRDTOOL_ARCHIVES)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', '-d', required=True, help='RRDtool database')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    create_database(args.database)


if __name__ == '__main__':
    main()
