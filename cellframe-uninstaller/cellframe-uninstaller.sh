#!/usr/bin/env bash
set -e

INSTALL_PATH="/opt/cellframe-node"
BACKUP="/opt/cellframe_backup/"
WALLET_FILES="/opt/cellframe-node/var/lib/wallet/*"


function check_root() {
    echo "[INFO] Checking if you're root..."
    if [[ $EUID -ne 0 ]] ; then
        echo "[ERROR] This script must be run as root. Exiting..." 
        exit 1
    else
        create_backup
    fi
}

function create_backup() {
    if [[ $(ls ${WALLET_FILES} 2> /dev/null) ]] ; then
        echo "[INFO] Detected .dwallet file(s), doing a backup..."
        mkdir -p ${BACKUP}
        cp ${WALLET_FILES} ${BACKUP}
        echo "[INFO] Wallet backup is now available at ${BACKUP}"
        wipe
    else
        wipe
    fi

}

function wipe() {
    if [[ $(dpkg -l | grep -i cellframe-node) ]] ; then
        echo "[INFO] Cellframe node is installed, removing it..."
        apt-get -yqq remove --purge cellframe-node
    fi

    if [[ -e ${INSTALL_PATH} ]] ; then
        echo "[INFO] Found ${INSTALL_PATH}, removing it..."
        rm -rf ${INSTALL_PATH}
        echo "[INFO] ${INSTALL_PATH} removed."
        echo "[INFO] You may now start from the beginning and do a fresh install of Cellframe node"
    fi
}

check_root