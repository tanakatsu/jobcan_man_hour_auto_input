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
    if rest.total_seconds() < 0:
        # sum of task hours is greater than total hour
        return None
    rest = str(rest)[:-3]
    return rest


parser = ArgumentParser()
parser.add_argument('csvfile', help='input csvfile')
parser.add_argument('-t', '--test', action='store_true', help='test mode')
parser.add_argument('--close_on_success', action='store_true', help='close browser on success')
parser.add_argument('--headless', action='store_true', help='headless mode')
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

# Check values
if not CHROMEDRIVER_PATH:
    raise ValueError("CHROMEDRIVER_PATH is empty")
if not CLIENT_ID:
    raise ValueError("CLIENT_ID is empty")
if not EMAIL:
    raise ValueError("EMAIL is empty")
if not PASSWORD:
    raise ValueError("PASSWORD is empty")

df = pd.read_csv(args.csvfile, dtype=str)
data_cols = [col for col in df.columns if col not in RESERVED_COLS]

testmode = args.test
close_on_success = args.close_on_success
headless = args.headless

if not testmode:
    jobcan_cli = JobcanInput(CHROMEDRIVER_PATH, client_id=CLIENT_ID, email=EMAIL, password=PASSWORD, headless=headless)
    jobcan_cli.login()
    jobcan_cli.open_man_hour_manage()

for i, row in df.iterrows():
    date = row['date']
    if all([type(row[col]) is float for col in data_cols]):
        print(f"{date}: no need to change")
        continue

    if not testmode:
        target_year, target_month = [int(t) for t in date.split("/")[:2]]
        current_year, current_month = jobcan_cli.get_current_year_and_month()
        if (not target_year == current_year) or (not target_month == current_month):
            jobcan_cli.set_current_year_and_month(target_year, target_month)

        total_work_time, total_man_hour = jobcan_cli.select_date(date, open=False)
        print(date, total_work_time, total_man_hour)
        if total_work_time == total_man_hour:
            # print(f"{date}: done")
            continue
        if total_work_time == "00:00":
            print(f"{date}: zero time")
            continue

    task_hours = []
    for col in data_cols:
        project_task = col.split("_")
        if len(project_task) == 2:
            project, task = project_task
        else:
            project = project_task[0]
            task = '_'.join(project_task[1:])
        hour = row[col]
        if type(hour) is str:
            task_hours.append(hour)

    if not testmode:
        rest_hour = calc_rest_of_hour(total_work_time, task_hours, row, data_cols)
        if rest_hour is None:
            print(f"{date}: [Error] total hour is greater than total work time")
            continue
        jobcan_cli.select_date(date, open=True)

    for col in data_cols:
        project_task = col.split("_")
        if len(project_task) == 2:
            project, task = project_task
        else:
            project = project_task[0]
            task = '_'.join(project_task[1:])
        hour = row[col]
        if type(hour) is str:
            if not testmode:
                if hour == '-1':
                    hour = rest_hour
                    print(date, project, task, -1, hour)
                else:
                    print(date, project, task, hour)
            else:
                print(date, project, task, hour)

            if not testmode:
                index = jobcan_cli.add_blank_record()
                jobcan_cli.input_data(index - 1, project, task, hour)

    if not testmode:
        # Trick. Without this code, last input will be saved as 00:00
        index = jobcan_cli.add_blank_record()
        jobcan_cli.input_data(index - 1, "⑤その他", "－", "0:00")

        jobcan_cli.save_data()
        jobcan_cli.wait_save_completed()

if not testmode:
    # after check
    unprocessed = 0
    for i, row in df.iterrows():
        date = row['date']
        target_year, target_month = [int(t) for t in date.split("/")[:2]]
        current_year, current_month = jobcan_cli.get_current_year_and_month()
        if (not target_year == current_year) or (not target_month == current_month):
            jobcan_cli.set_current_year_and_month(target_year, target_month)

        total_work_time, total_man_hour = jobcan_cli.select_date(date, open=False)
        if not total_work_time == "00:00":  # working day
            if not total_work_time == total_man_hour:  # not processed day
                print(f"{date}: [Warning] Unprocessed. Check again")
                unprocessed += 1
                continue
    if unprocessed == 0:
        print("All dates are processed")
        if close_on_success:
            jobcan_cli.quit()
