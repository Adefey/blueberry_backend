#!/bin/bash

set -e 

javac -d ./build ./src/*.java

cd ./build

java Main