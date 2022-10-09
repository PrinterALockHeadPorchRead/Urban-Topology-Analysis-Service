#!/bin/bash

export LOGS_DIRECTORY="$1/"

docker compose up --build

docker rmi $(docker images -f 'dangling=true' -q)