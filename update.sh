#!/usr/bin/bash

sudo docker-compose down -v
git pull
sudo docker-compose up -d --build