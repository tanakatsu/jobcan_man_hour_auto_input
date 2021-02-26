if [ $# != 1 ]; then
  echo Usage: jobcan_auto_input.sh your_monthly.csv
  exit 1
fi

csvfile=$1
python validate_monthly_csv.py $csvfile
status=$?
if [ $status -eq 1 ]; then
  exit 1
fi
python auto_input.py $csvfile
