#!/bin/bash

set -e

docker run --rm -v ${PWD}:/app -e JOBCAN_CHROMEDRIVER_PATH=/opt/chrome/chromedriver -e JOBCAN_CLIENT_ID=${JOBCAN_CLIENT_ID} -e JOBCAN_EMAIL=${JOBCAN_EMAIL} -e JOBCAN_PASSWORD=${JOBCAN_PASSWORD} jobcan-autoinput python generate_projects_and_tasks.py --headless
