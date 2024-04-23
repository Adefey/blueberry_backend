#!/usr/bin/bash

docker-compose down -v
git pull
docker-compose up -d --build
