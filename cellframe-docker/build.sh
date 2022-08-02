#!/bin/bash

if [[ ! $# -eq 0 ]] ; then
    docker build -t "$1" .
else
    echo "Usage: ./build.sh <name>"
fi