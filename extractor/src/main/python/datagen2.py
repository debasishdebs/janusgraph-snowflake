#!./python/bin/python

import argparse
import re
from datetime import datetime
from datetime import timedelta
import datagenlib as dg
import common.utils
from common.resources import Resources as R
import json, os


def main():
    parser = argparse.ArgumentParser(description='Generate sample data')
    parser.add_argument('config', type=argparse.FileType('r'), help='Config file')
#    parser.add_argument('--write', type=argparse.FileType('w'), default='-', help='Write to file')
    parser.add_argument('--period', default='1h', help='Generate data for N last days [suffix d] or last N hours [suffix h] or last N minutes [suffix m]')
    args = parser.parse_args()
    matches = re.match('(\d+)([dhm])', args.period)

    input_config = os.path.basename(os.path.abspath(args.config.name))
    cfg_fname = input_config.split(".")[0]
    R.put_ds(cfg_fname)

    if not matches:
        parser.print_help()

    period = int(matches.group(1))
    period_type = matches.group(2)
    end_date = datetime.now()

    if period_type == 'h':
        beg_date = end_date - timedelta(hours=period)
    elif period_type == 'm':
        beg_date = end_date - timedelta(minutes=period)

    if period_type == 'd':
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        beg_date = end_date - timedelta(days=period)

    clock = dg.Clock(beg_date, end_date)
    users = dg.load_model_from_file(args.config)
    for u in users:
        clock.add_observer(u)
    while clock.tick():
        pass

    data = R.get_data()
    print("Rows: ", len(data))

    period = args.period
    today = datetime.now().date().strftime("%Y_%m_%d")
    out_fname = f"{cfg_fname}_{period}_{today}.json"

    json.dump(data, open(os.path.abspath(f"../../../target/{out_fname}"), "w+"), indent=1)

    print(out_fname)


if __name__ == '__main__':
    # python datagen2.py ../config/windowsnxlog_phishing_attack.yaml --period 1d
    main()
