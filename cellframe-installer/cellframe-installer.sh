#!/usr/bin/env bash
set -e

ARCH=`uname -m`
CODENAME=`lsb_release -cs 2> /dev/null`

function display_information() {
    echo "This script will install the latest Cellframe node available for your distribution."
    read -r -p "Press enter now to continue or CTRL+C to abort."
}

function test_deps() {
    echo "[INFO] Testing if you have wget installed on your operating system..."
    if [[ ! $(which wget) ]] ; then
        echo "[INFO] wget binary not found. Installing wget..."
        apt-get -qq update && apt-get -yqq install wget
        export REMOVE_DEPS="wget"
    else
        echo "[INFO] wget found..."
    fi

    echo "[INFO] Testing if you have gnupg installed on your operating system..."
    if [[ ! $(which gpg) ]] ; then
        echo "[INFO] gnupg not found. Installing gnupg..."
        apt-get -qq update && apt-get -yqq install gnupg
        export REMOVE_DEPS="${REMOVE_DEPS} gnupg"
    else
        echo "[INFO] gnupg found..."
    fi

    echo "[INFO] Testing if you have curl installed on your operating system..."
    if [[ ! $(which curl) ]] ; then
        echo "[INFO] curl not found. Installing curl..."
        apt-get -qq update && apt-get -yqq install curl
        export REMOVE_DEPS="${REMOVE_DEPS} curl"
    else
        echo "[INFO] curl found..."
    fi
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
    elif [[ ${CODENAME} == "bookworm" || ${CODENAME} == "elsie" ]] ; then
        echo "[INFO] ${CODENAME} is supported. Continuing..." #Linux Mint elsie == bullseye, for bookworm we can use bullseye repo
        export CODENAME="bullseye"
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

    if [[ ${ARCH} == "x86_64" ]] ; then
        export DOWNLOAD_ARCH="amd64"
    elif [[ ${ARCH} == "aarch64" ]] ; then
        export DOWNLOAD_ARCH="arm64"
    fi

    if [[ ${ARCH} == "aarch64" && ${CODENAME} != "bullseye" ]] ; then
        echo "[ERROR] Detected ${ARCH} platform but there's no package for your distro at Demlabs repository. Exiting..."
        exit 5
    fi
}

function check_node_installation() {
    if [[ $(which cellframe-node) || $(which cellframe-node-cli) || -e /opt/cellframe-node/bin/cellframe-node ]] ; then
        echo "[ERROR] Looks like you have Cellframe node already installed. Exiting..."
        exit 6
    else
        echo "[INFO] Didn't find installed Cellframe node. Continuing..."
    fi
}

function do_upgrade() {
    echo "[INFO] Installing system updates..."
    apt-get -qq update && apt-get -yqq dist-upgrade
    prompt_bleeding_edge
}

function prompt_bleeding_edge() {
    echo "[INFO] You can try the latest 5.1 branch version also which has support for mainnet (Backbone)."
    read -r -p "[INFO] Do you want to install the 5.1 release version (unstable)? [y/N] " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]] ; then
        download_and_install_latest
    else
        setup_pubkey
    fi
}

function download_and_install_latest() {
    echo "[INFO] Downloading latest 5.1-xx release from pub.cellframe.net"
    LATEST_VERSION_ARM64=$(curl 'https://pub.cellframe.net/linux/release-5.1/?C=M&O=D' | grep -oP 'href="\Kcellframe-node-\d.\d.\d*-arm64' | head -n1)
    LATEST_VERSION_AMD64=$(curl 'https://pub.cellframe.net/linux/release-5.1/?C=M&O=D' | grep -oP 'href="\Kcellframe-node-\d.\d.\d*-amd64' | head -n1)
    if [[ ${DOWNLOAD_ARCH} == "amd64" ]] ; then
        wget -q https://pub.cellframe.net/linux/release-5.1/${LATEST_VERSION_AMD64}.deb > /dev/null
        dpkg -i ${LATEST_VERSION_AMD64}.deb
        rm ${LATEST_VERSION_AMD64}.deb
        prompt_plugins
    elif [[ ${DOWNLOAD_ARCH} == "arm64" ]] ; then
        wget -q https://pub.cellframe.net/linux/release-5.1/${LATEST_VERSION_ARM64}.deb > /dev/null
        dpkg -i ${LATEST_VERSION_ARM64}.deb
        rm ${LATEST_VERSION_ARM64}.deb
        prompt_plugins
    else
        echo "[ERROR] Couldn't determine which platform you are using. Exiting."
        exit 8
    fi
}

function setup_pubkey() {
    echo "[INFO] Setting up Demlabs public key..."
    wget -q -O- https://debian.pub.demlabs.net/public/public-key.gpg | gpg --dearmor | tee /usr/share/keyrings/demlabs-archive-keyring.gpg > /dev/null
    add_repo
}

function add_repo() {
    echo "[INFO] Adding Demlabs repository to known sources..."
    echo "deb [signed-by=/usr/share/keyrings/demlabs-archive-keyring.gpg] https://debian.pub.demlabs.net/public ${CODENAME} main" > /etc/apt/sources.list.d/demlabs.list
    install_node
}

function install_node() {
    echo "[INFO] Installing Cellframe node, you need to answer the questions what installer asks during the installation..."
    apt-get -qq update && apt-get -yqq install cellframe-node
    prompt_plugins
}

function prompt_plugins() {
    read -r -p "[INFO] Do you want to enable Cellframe node Python plugins? [y/N] " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]] ; then
        enable_plugins
    else
        prompt_remove_deps
    fi
}

function prompt_remove_deps() {
    if [[ ! -z ${REMOVE_DEPS} ]] ; then
        read -r -p "[INFO] Do you want remove the installed packages which were installed during setup (${REMOVE_DEPS})? [y/N] " response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]] ; then
            apt purge -yqq ${REMOVE_DEPS}
            recommend_reboot
        else
            recommend_reboot
        fi
    else
        recommend_reboot
    fi
}

function enable_plugins() {
    if [[ -e /opt/cellframe-node/etc/cellframe-node.cfg ]] ; then
        echo "[INFO] Enabling Python plugins..."
        sed -i 's/#\[plugins\]/\[plugins\]/g' /opt/cellframe-node/etc/cellframe-node.cfg
        sed -i 's/#py_load=.*/py_load=true/g' /opt/cellframe-node/etc/cellframe-node.cfg
        sed -i 's/#py_path=.*/py_path=\/opt\/cellframe-node\/var\/lib\/plugins/g' /opt/cellframe-node/etc/cellframe-node.cfg
        prompt_remove_deps
    else
        echo "[ERROR] Configuration file is missing. Error in installation?"
        exit 7
    fi
}

function recommend_reboot() {
    echo "[INFO] Now it's recommended to reboot your computer."
    read -r -p "[INFO] If you wish to automatically do that, just press enter. Otherwise, press CTRL+C"
    reboot 
}

check_root
display_information
test_deps
check_lsb_release
check_distro
check_arch
check_node_installation
do_upgrade
prompt_bleeding_edge
