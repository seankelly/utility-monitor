#!/usr/bin/env python3

import argparse
import json
import os.path
import subprocess
import sys

import rrdtool


RRDTOOL_SOURCES = [
    # Heartbeat of 900 means maximum of 15 minutes before UNKNOWN value.
    'DS:decawatts:COUNTER:900:0:U',
]
RRDTOOL_ARCHIVES = [
    # Three months (95 days) of every 15 minutes.
    'RRA:AVERAGE:0.3:3:9200',
    # Five years of hourly data.
    'RRA:AVERAGE:0.5:12:44000',
]


def create_database(database_path):
    if os.path.exists(database_path):
        return
    rrdtool.create(database_path, RRDTOOL_SOURCES, RRDTOOL_ARCHIVES)


def rrdtool_add_sample(database_path, meter_reading):
    consumption = meter_reading['Message']['LastConsumptionCount']
    rrdtool.update(database_path, 'N:' + str(consumption))


def rtl_tcp_one_shot(rtl_tcp_server=None, filterid=None):
    rtlamr_cmd = ['timeout', '200',
                  'rtlamr', '-msgtype', 'idm', '-format', 'json', '-single']
    if rtl_tcp_server:
        rtlamr_cmd.extend(['-server', rtl_tcp_server])
    if filterid:
        rtlamr_cmd.extend(['-filterid', filterid])
    rtlamr = subprocess.Popen(rtlamr_cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    stdout, stderr = rtlamr.communicate()
    if rtlamr.returncode != 0:
        raise RuntimeError(f"Failed to run rtlamr: {stderr}")
    meter_idm = json.loads(stdout)
    return meter_idm


def read_input_file(input_file):
    if not os.path.exists(input_file):
        print(f"Could not access input file: {input_file}")
        return
    with open(input_file) as input_data:
        meter_reading = json.load(input_data)
        return meter_reading


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', '-d', required=True, help='RRDtool database')
    parser.add_argument('--input', '-i', help='Input file')
    parser.add_argument('--filterid', '-I', help="Filter on this meter ID")
    parser.add_argument('--server', '-s', help="rtl_tcp server")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    create_database(args.database)

    if args.input:
        sample = read_input_file(args.input)
    else:
        sample = rtl_tcp_one_shot(args.server, args.filterid)
    rrdtool_add_sample(args.database, sample)


if __name__ == '__main__':
    main()
