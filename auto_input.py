from lib.jobcan import JobcanInput
import pandas as pd
from datetime import timedelta
from argparse import ArgumentParser
import os
import re


RESERVED_COLS = ["date"]


def calc_rest_of_hour(total_hour, task_hours, row, cols):
    hour, minute = [int(t) for t in total_hour.split(":")]
    total = timedelta(hours=hour, minutes=minute)
    rest = total
    for col in cols:
        val = row[col]
        if type(val) is str:
            if re.match("\d\d:\d\d", val) or re.match("\d:\d\d", val):
                h, m = [int(t) for t in val.split(":")]
                rest = rest - timedelta(hours=h, minutes=m)
    rest = str(rest)[:-3]
    return rest


parser = ArgumentParser()
parser.add_argument('csvfile', help='input csvfile')
parser.add_argument('-t', '--test', action='store_true', help='test mode')
parser.add_argument('--chrome_driver_path', help='chrome driver path')
parser.add_argument('--client_id', help='client_id')
parser.add_argument('--email', help='email')
parser.add_argument('--password', help='password')
args = parser.parse_args()

# Get credentials
CHROMEDRIVER_PATH = args.chrome_driver_path if args.chrome_driver_path else os.environ.get('JOBCAN_CHROMEDRIVER_PATH')
CLIENT_ID = args.client_id if args.client_id else os.environ.get('JOBCAN_CLIENT_ID')
EMAIL = args.email if args.email else os.environ.get('JOBCAN_EMAIL')
PASSWORD = args.password if args.password else os.environ.get('JOBCAN_PASSWORD')

df = pd.read_csv(args.csvfile, dtype=str)
data_cols = [col for col in df.columns if col not in RESERVED_COLS]

testmode = args.test
if not testmode:
    jobcan_cli = JobcanInput(CHROMEDRIVER_PATH, client_id=CLIENT_ID, email=EMAIL, password=PASSWORD)
    jobcan_cli.login()
    jobcan_cli.open_man_hour_manage()

for i, row in df.iterrows():
    date = row['date']
    if all([type(row[col]) is float for col in data_cols]):
        print(f"{date}: no need to change")
        continue

    if not testmode:
        total_work_time, total_man_hour = jobcan_cli.select_date(date, open=False)
        print(date, total_work_time, total_man_hour)
        if total_work_time == total_man_hour:
            print(f"{date}: done")
            continue
        if total_work_time == "00:00":
            print(f"{date}: zero time")
            continue

    task_hours = []
    for col in data_cols:
        project, task = col.split("_")
        hour = row[col]
        if type(hour) is str:
            task_hours.append(hour)

    if not testmode:
        jobcan_cli.select_date(date, open=True)

    for col in data_cols:
        project, task = col.split("_")
        hour = row[col]
        if type(hour) is str:
            if not testmode:
                if hour == '-1':
                    hour = calc_rest_of_hour(total_work_time, task_hours, row, data_cols)
                    print(date, project, task, -1, hour)
                else:
                    print(date, project, task, hour)
            else:
                print(date, project, task, hour)

            if not testmode:
                index = jobcan_cli.add_blank_record()
                jobcan_cli.input_data(index - 1, project, task, hour)

    if not testmode:
        jobcan_cli.save_data()
        jobcan_cli.wait_save_completed()

if not testmode:
    jobcan_cli.quit()
