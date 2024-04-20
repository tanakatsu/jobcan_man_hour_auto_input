from lib.jobcan import JobcanInput
import pandas as pd
from argparse import ArgumentParser
import os

parser = ArgumentParser()
parser.add_argument('--chrome_driver_path', help='chrome driver path')
parser.add_argument('-o', '--output', type=str, default="project_task.all.csv", help='output filename')
parser.add_argument('--client_id', help='client_id')
parser.add_argument('--email', help='email')
parser.add_argument('--password', help='password')
parser.add_argument('--headless', action='store_true', help='headless mode')
args = parser.parse_args()

# Get credentials
CHROMEDRIVER_PATH = args.chrome_driver_path if args.chrome_driver_path else os.environ.get('JOBCAN_CHROMEDRIVER_PATH')
CLIENT_ID = args.client_id if args.client_id else os.environ.get('JOBCAN_CLIENT_ID')
EMAIL = args.email if args.email else os.environ.get('JOBCAN_EMAIL')
PASSWORD = args.password if args.password else os.environ.get('JOBCAN_PASSWORD')
headless = args.headless

# Retrieve projects and tasks list
jobcan_cli = JobcanInput(CHROMEDRIVER_PATH, client_id=CLIENT_ID, email=EMAIL, password=PASSWORD, headless=headless)
jobcan_cli.login()
jobcan_cli.open_man_hour_manage()
jobcan_cli.select_date(open=True)
jobcan_cli.add_blank_record()
projects_and_tasks = jobcan_cli.get_projects_and_tasks()
jobcan_cli.quit()
print(projects_and_tasks)

# create csv file
data = {"project": [], "task": []}
for project, tasks in projects_and_tasks.items():
    for task in tasks:
        data["project"].append(project)
        data["task"].append(task)
df = pd.DataFrame(data)
df.to_csv(args.output, index=False)
