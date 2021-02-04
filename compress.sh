#!/bin/bash

BASE_DIR="/home/bijutiju/reddit_client"
[[ -z "${BASE_DIR}" ]] && echo "Please update BASE_DIR in ${0}." && exit 1

find "${BASE_DIR}/data" -type f -mmin +30 -exec gzip {} \;
