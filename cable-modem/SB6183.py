#!/usr/bin/env python3

import argparse
import json
import sys
from datetime import datetime

from bs4 import BeautifulSoup
import requests


DEFAULT_STATUS_URL = 'http://192.168.100.1/RgConnect.asp'


class SB6183Modem():

    def __init__(self, modem_url, output_format):
        self.modem_url = modem_url
        self.output_format = output_format

    def parse_modem(self):
        try:
            resp = requests.get(self.modem_url)
            status_html = resp.content
            resp.close()
            soup = BeautifulSoup(status_html, 'html.parser')
        except Exception as exc:
            print('ERROR: Failed to get modem stats.  Aborting', file=sys.stderr)
            print(exc, file=sys.stderr)
            sys.exit(1)

        series = []
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        # downstream table
        for table_row in soup.find_all("table")[2].find_all("tr")[2:]:
            if table_row.th:
                continue
            row_columns = table_row.find_all('td')
            channel = row_columns[0].text.strip()
            channel_id = row_columns[3].text.strip()
            frequency = row_columns[4].text.replace(" Hz", "").strip()
            power = row_columns[5].text.replace(" dBmV", "").strip()
            snr = row_columns[6].text.replace(" dB", "").strip()
            corrected = row_columns[7].text.strip()
            uncorrectables = row_columns[8].text.strip()

            downstream_result_dict = {
                'measurement': 'cable_modem',
                'time': current_time,
                'fields': {
                    'channel_id': int(channel_id),
                    'frequency': int(frequency),
                    'power': float(power),
                    'snr': float(snr),
                    'corrected': int(corrected),
                    'uncorrectables': int(uncorrectables),
                },
                'tags': {
                    'channel': int(channel),
                    'direction': 'downstream',
                }
            }
            series.append(downstream_result_dict)

        # upstream table
        for table_row in soup.find_all("table")[3].find_all("tr")[2:]:
            if table_row.th:
                continue
            row_columns = table_row.find_all('td')
            channel = row_columns[0].text.strip()
            channel_id = row_columns[3].text.strip()
            frequency = row_columns[5].text.replace(" Hz", "").strip()
            power = row_columns[6].text.replace(" dBmV", "").strip()

            upstream_result_dict = {
                'measurement': 'cable_modem',
                'time': current_time,
                'fields': {
                    'channel_id': int(channel_id),
                    'frequency': int(frequency),
                    'power': float(power),
                    'snr': float(snr),
                },
                'tags': {
                    'channel': int(channel),
                    'direction': 'upstream',
                }
            }
            series.append(upstream_result_dict)
        return series

    def output_modem_data(self, series):
        if self.output_format == 'influx':
            for point in series:
                tags = ['%s=%s' % (tag, value)
                        for tag, value in point['tags'].items()]
                fields = ['%s=%s' % (field, value)
                          for field, value in point['fields'].items()]
                line_protocol = '{measurement},{tags} {fields} {when}'.format(
                    measurement=point['measurement'], when=point['time'],
                    tags=','.join(tags), fields=','.join(fields))
                print(line_protocol)
        else:
            json.dump(series, sys.stdout)

    def run(self):
        modem_stats = self.parse_modem()
        self.output_modem_data(modem_stats)


def main():
    parser = argparse.ArgumentParser(description="A tool to scrape modem statistics")
    parser.add_argument('--url', default=DEFAULT_STATUS_URL,
                        help="URL to modem status page")
    parser.add_argument('--format', default='influx', choices=('influx', 'json'),
                        help='Output format, default of "influx"')
    args = parser.parse_args()
    collector = SB6183Modem(args.url, args.format)
    collector.run()


if __name__ == '__main__':
    main()
