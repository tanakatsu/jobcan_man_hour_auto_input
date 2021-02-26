import pandas as pd
from calendar import monthrange
from datetime import date, datetime
from argparse import ArgumentParser

PROJECT_TASK_CSVFILE = "project_task.csv"

def main():
    parser = ArgumentParser()
    parser.add_argument('year', type=int, help='year')
    parser.add_argument('month', type=int, help='month')
    args = parser.parse_args()
    year = args.year
    month = args.month

    df_project = pd.read_csv(PROJECT_TASK_CSVFILE)
    columns = ['date']
    for _, row in df_project.iterrows():
        project = row['project']
        task = row['task']
        col = f"{project}_{task}"
        columns.append(col)

    csv_data = {}
    for col in columns:
        csv_data[col] = []

    _, last_day = monthrange(year, month)
    for day in range(1, last_day + 1):
        csv_data['date'].append("{:04d}/{:02d}/{:02d}".format(year, month, day))
        for col in columns:
            if col == "date":
                continue
            csv_data[col].append(None)

    df_out = pd.DataFrame(csv_data, columns=columns)
    df_out.set_index('date')
    output_csv = "{:04d}_{:02d}.csv".format(year, month)
    df_out.to_csv(output_csv, index=False)


if __name__ == "__main__":
    main()
