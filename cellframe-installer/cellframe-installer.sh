#!/bin/bash

DEPS="wget gnupg libpython3.9 libmagic1"
ARCH=`uname -m`
CODENAME=`lsb_release -cs`

function display_information() {
    echo "This script will install the latest Cellframe node available for your distribution."
    read -r -p "Press enter now to continue or CTRL+C to abort."
}

function check_root() {
    echo "[INFO] Checking if you're root..."
    if [[ $EUID -ne 0 ]] ; then
        echo "[ERROR] This script must be run as root. Exiting..." 
        exit 1
    fi
}

function check_lsb_release() {
    echo "[INFO] Checking lsb_release availability..."
    if  [[ ! $(which lsb_release) ]] ; then
        echo "[ERROR] lsb_release not found. Install it with apt install lsb-release"
        exit 2
    else
        echo "[INFO] lsb_release found. Continuing..."
    fi
}

function check_distro() {
    echo "[INFO] Checking if your Linux distro is compatible..."
    if [[ ${CODENAME} == "focal" || ${CODENAME} == "bullseye" ]] ; then
        echo "[INFO] ${CODENAME} is supported. Continuing..."
    else
        echo "[ERROR] ${CODENAME} is not supported. Exiting..."
        exit 3
    fi
}

function check_arch() {
    echo "[INFO] Checking architecture compatibility..."
    if [[ ${ARCH} == "x86_64" || ${ARCH} == "aarch64" ]] ; then
        echo "[INFO] ${ARCH} is supported. Continuing... "
    else
        echo "[ERROR] ${ARCH} is not supported. Exiting..."
        exit 4
    fi
    
    if [[ ${ARCH} == "aarch64" && ${CODENAME} != "bullseye" ]] ; then
        echo "[ERROR] Detected ${ARCH} platform but there's no package for your distro at Demlabs repository. Exiting..."
        exit 5
    fi
}

function install_dependencies() {
    echo "[INFO] Installing dependencies..."
    apt-get -qq update && apt-get -yqq install ${DEPS} && apt-get -yqq dist-upgrade
}

function setup_pubkey() {
    echo "[INFO] Setting up Demlabs public key..."
    wget -q -O- https://debian.pub.demlabs.net/public/public-key.gpg | gpg --dearmor | tee /usr/share/keyrings/demlabs-archive-keyring.gpg > /dev/null
}

function add_repo() {
    echo "[INFO] Adding Demlabs repository to known sources..."
    echo "deb [signed-by=/usr/share/keyrings/demlabs-archive-keyring.gpg] https://debian.pub.demlabs.net/public ${CODENAME} main" > /etc/apt/sources.list.d/demlabs.list
}

function install_node() {
    echo "[INFO] Installing Cellframe node..."
    apt-get -qq update && apt-get -yqq install cellframe-node
}

function recommend_reboot() {
    echo "[INFO] Now it's recommended to reboot your computer."
    read -r -p "[INFO] If you wish to automatically do that, just press enter. Otherwise, press CTRL+C"
    reboot 
}

display_information
check_root
check_lsb_release
check_distro
check_arch
install_dependencies
setup_pubkey
add_repo
install_node
recommend_reboot