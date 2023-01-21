#!/bin/bash

export LC_ALL=C

settings=("${HOME}/Cellframe/cellframe-sdk|origin/master|origin/develop"
       "${HOME}/Cellframe/cellframe-node|origin/master|origin/develop"
       "${HOME}/Cellframe/python-cellframe|origin/master|origin/develop"
       "${HOME}/Cellframe/cellframe-dashboard|origin/master|origin/develop"
       "${HOME}/Cellframe/cellframe-wallet|origin/main|origin/develop")

read -p "From how many days? " days

regex='^[0-9]+'

if ! [[ $days =~ $regex ]] ; then
    days=21 #3 weeks is default
    echo "Invalid input, using default of ${days} days..."
fi

date=$(date "+%b %d %Y" -d "-${days} days")

for data in ${settings[@]}
do
    path=$(echo ${data} | cut -f1 -d'|')
    master_branch=$(echo ${data} | cut -f2 -d'|')
    dev_branch=$(echo ${data} | cut -f3 -d'|')
    
    if [[ -d "${path}" ]] ; then
        cd "${path}"
        commits_master=$(git rev-list --count ${master_branch} --since="${date}")
        commits_dev=$(git rev-list --count ${dev_branch} --since="${date}")
        commits_all=$(git rev-list --count --since="${date}" --all)
        strip_path=$(basename "${path}")
        echo -e "\n${strip_path^^}:\n
        ${commits_master} commits in master branch in last ${days} days\n
        ${commits_dev} commits in development branch in last ${days} days\n
        ${commits_all} commits in all branches in last ${days} days.\n"
    else
        echo "Path ${path} does not exist!"
    fi

done