#!/bin/bash

cp template.yaml docker-compose.yaml

sed -i "s+LOGS_DIR+$1+g" docker-compose.yaml

docker compose up --build

docker rmi $(docker images -f 'dangling=true' -q)

docker compose down
