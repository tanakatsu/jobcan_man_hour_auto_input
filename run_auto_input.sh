#!/bin/bash

set -e

if [ $# != 1 ]; then
  echo Usage: run_auto_input.sh your_monthly.csv
  exit 1
fi

csvfile=$1
docker run --rm -v ${PWD}:/app -e JOBCAN_CHROMEDRIVER_PATH=/opt/chrome/chromedriver -e JOBCAN_CLIENT_ID=${JOBCAN_CLIENT_ID} -e JOBCAN_EMAIL=${JOBCAN_EMAIL} -e JOBCAN_PASSWORD=${JOBCAN_PASSWORD} jobcan-autoinput ./jobcan_auto_input_headless.sh $csvfile
