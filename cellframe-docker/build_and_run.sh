#!/bin/bash

if [[ $# -lt 1 ]] ; then
    echo "Usage: ./build_and_run.sh <name> [-d] (-d for daemonizing)"
    exit 1
    
elif [[ $# -eq 2 ]]; then
    if [[ "$2" != "-d" ]] ; then
            echo "Unsupported argument: $2, exiting..."
            exit 1
    else
        docker build -t "$1" .
        docker volume create "$1"
        docker run -v "$1":/opt/cellframe-node --name="$1" --privileged --net=host -it -d "$1" 
    fi

else
    docker build -t "$1" .
    docker volume create "$1"
    docker run -v "$1":/opt/cellframe-node --name="$1" --privileged --net=host -it "$1"
fi