#!/bin/bash

BASE_DIR="/home/bijutiju/reddit_client"

[[ -z "${BASE_DIR}" ]] && echo "Please update BASE_DIR in ${0}." && exit 1

source "${BASE_DIR}/venv/bin/activate"
source "${BASE_DIR}/.env.sh"

python "${BASE_DIR}/reddit_stream_client.py" --reddit wallstreetbets --type comments --save
