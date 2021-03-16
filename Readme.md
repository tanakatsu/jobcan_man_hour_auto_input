## Jobcan man hour auto input tool

### What is this ?

This is a tool that helps inputting man-hour records repeatedly.
Save time and work more :-)

### System requirements
- Python
- Chrome browser

### Get started

1. Install required python packages
    ```
    $ pip install pandas
    $ pip install selenium
    ```
1. Download ChromeDriver
    - Check your chrome browser's version
    - Download appropriate ChromeDriver from [here](https://chromedriver.chromium.org/downloads)
    - Unzip and put `chromedriver` into suitable location
1. Set crendential information and chrome driver's path
    ```
    export JOBCAN_CHROMEDRIVER_PATH=PATH_TO_YOUR_DRIVER_PATH
    export JOBCAN_CLIENT_ID=YOUR_COMPANY_CLIENT_ID
    export JOBCAN_EMAIL=YOUR_EMAIL
    export JOBCAN_PASSWORD=YOUR_PASSWORD
    ```
1. Generate project and task csv
    ```
    $ python generate_projects_and_tasks.py
    ```
1. Generate monthly csv
    ```
    # Example
    $ python generate_monthly_csv.py 2021 3
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
    ./jobcan_auto_input.sh 2021_03.csv
    ```

### License
MIT
