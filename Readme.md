## Jobcan man hour auto input tool

### What is this ?

This is a tool that helps inputting man-hour records repeatedly.
Save time and work more :-)

### System requirements
- Docker

### Get started

1. Build docker image
    ```
    ./build.sh
    ```
1. Set crendential information and chrome driver's path
    ```
    export JOBCAN_CHROMEDRIVER_PATH=PATH_TO_YOUR_DRIVER_PATH
    export JOBCAN_CLIENT_ID=YOUR_COMPANY_CLIENT_ID
    export JOBCAN_EMAIL=YOUR_EMAIL
    export JOBCAN_PASSWORD=YOUR_PASSWORD
    ```
1. Generate project and task csv
    ```
    $ ./run_generate_projects_and_tasks.py
    ```
1. Copy project\_task.all.csv and edit project\_task.csv to drop irrelevant tasks to you
    ```
    $ cp project_task.all.csv project_task.csv
    ```
1. Generate monthly csv
    ```
    # Example
    $ ./run_generate_monthly_csv.sh 2021 3
    ```
1. Edit monthly csv
    ```
    # Example
    date,プロジェクト1_タスクA,プロジェクト2_タスクB,プロジェクト2_タスクC
    2021/03/01,1:00,6:00,1:00
    2021/03/02,1:00,,7:00
    2021/03/03,-1,1:00,1:00
    ```
    - "-1" is a special keyword that means "rest of hours"
    - In above example, -1 would be 6:00 when total work hours is 8:00
1. Run auto input tool
    ```
    ./run_auto_input.sh 2021_03.csv
    ```

### License
MIT
