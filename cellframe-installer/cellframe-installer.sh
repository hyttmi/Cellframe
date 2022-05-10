#!/usr/bin/env bash
set -e

ARCH=`uname -m`
CODENAME=`lsb_release -cs 2> /dev/null`

function check_root() {
    echo "[INFO] Checking if you're root..."
    if [[ $EUID -ne 0 ]] ; then
        echo "[ERROR] This script must be run as root. Exiting..." 
        exit 1
    else
        display_information
    fi
}

function display_information() {
    echo "[INFO] This script will install the latest Cellframe node available for your distribution."
    read -r -p "[INFO] Press enter now to continue or CTRL+C to abort."
    test_debian_based
}

function test_debian_based {
    echo "[INFO] Testing if you're running a Debian based distro..."
    if [[ $(which dpkg) ]] ; then
        echo "[INFO] Looks like you're running a Debian based distro"
        test_deps
    else
        echo "[ERROR] Debian based distro not detected. This script is only compatible with Debian based distros."
        exit 2
    fi
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

    echo "[INFO] Testing if you have lsb_release installed on your operating system..."
    if [[ ! $(which lsb_release) ]] ; then
        echo "[INFO] lsb_release not found. Installing lsb_release..."
        apt-get -qq update && apt-get -yqq install lsb-release
        export REMOVE_DEPS="${REMOVE_DEPS} lsb-release"
    else
        echo "[INFO] lsb_release found..."
    fi

    echo "[INFO] Testing if you have curl installed on your operating system..."
    if [[ ! $(which curl) ]] ; then
        echo "[INFO] curl not found. Installing curl..."
        apt-get -qq update && apt-get -yqq install curl
        export REMOVE_DEPS="${REMOVE_DEPS} curl"
        do_upgrade
    else
        echo "[INFO] curl found..."
        do_upgrade
    fi
}

function do_upgrade() {
    echo "[INFO] Installing system updates..."
    apt-get -qq update && apt-get -yqq dist-upgrade
    check_node_installation    
}

function check_node_installation() {
    if [[ $(which cellframe-node) || $(which cellframe-node-cli) || -e /opt/cellframe-node/bin/cellframe-node ]] ; then
        echo "[ERROR] Looks like you have Cellframe node already installed. Exiting..."
        exit 3
    else
        echo "[INFO] Didn't find installed Cellframe node. Continuing..."
        check_distro_and_arch
    fi
}

function check_distro_and_arch() {
    echo "[INFO] Checking architecture compatibility..."
    if [[ ${ARCH} == "x86_64" || ${ARCH} == "aarch64" ]] ; then
        echo "[INFO] ${ARCH} is supported. Continuing... "
    else
        echo "[ERROR] ${ARCH} is not supported. Exiting..."
        exit 4
    fi

    if [[ ${CODENAME} == "bullseye" ]] ; then
        echo "[INFO] ${CODENAME} is supported, continuing..."
        setup_pubkey
    elif [[ ${CODENAME} == "elsie" || ${CODENAME} == "bookworm" ]] ; then # We can use bullseye repo for bookworm and Linux Mint elsie.
        echo "[INFO] ${CODENAME} is supported, continuing..."
        export CODENAME="bullseye"
        setup_pubkey
    elif [[ ${CODENAME} == "focal" || ${CODENAME} == "hirsute" || ${CODENAME} == "stretch" || ${CODENAME} == "bionic" || ${CODENAME} == "buster" ]] ; then # All of these also available in repos, but only amd64
        if [[ ${ARCH} == "x86_64" ]] ; then
            echo "[INFO] ${CODENAME} is supported for ${ARCH} platforms, continuing..."
            setup_pubkey
        fi
    else
        echo "[INFO] ${CODENAME} is not supported. However, you can install the latest package manually as you are running Debian based distro."
        read -r -p "[INFO] Do you want to install the latest available Cellframe node version? [y/N] " response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]] ; then
            download_and_install_latest
        else
            echo "[INFO] As you wish, exiting..."
            exit 5
        fi
    fi
}

function download_and_install_latest() {
    echo "[INFO] Downloading latest Cellframe node..."
    if [[ ${ARCH} == "x86_64" ]] ; then
        DOWNLOAD_LINK=$(curl -s 'https://debian.pub.demlabs.net/public/pool/main/c/cellframe-node/?C=M;O=D' | grep -oP '(?<=href=").+?amd64.(deb)' | head -n1)
    else
        DOWNLOAD_LINK=$(curl -s 'https://debian.pub.demlabs.net/public/pool/main/c/cellframe-node/?C=M;O=D' | grep -oP '(?<=href=").+?arm64.(deb)' | head -n1)
    fi

    wget https://debian.pub.demlabs.net/public/pool/main/c/cellframe-node/${DOWNLOAD_LINK}
    echo "[INFO] Installing Cellframe node, you need to answer the questions what installer asks during the installation..."
    apt-get -yqq install ./${DOWNLOAD_LINK}
    rm ${DOWNLOAD_LINK}
    prompt_plugins
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

function enable_plugins() {
    if [[ -e /opt/cellframe-node/etc/cellframe-node.cfg ]] ; then
        echo "[INFO] Enabling Python plugins..."
        sed -i 's/#\[plugins\]/\[plugins\]/g' /opt/cellframe-node/etc/cellframe-node.cfg
        sed -i 's/#py_load=.*/py_load=true/g' /opt/cellframe-node/etc/cellframe-node.cfg
        sed -i 's|#py_path=.*|py_path=/opt/cellframe-node/var/lib/plugins|g' /opt/cellframe-node/etc/cellframe-node.cfg
        prompt_remove_deps
    else
        echo "[ERROR] Configuration file is missing. Error in installation?"
        exit 6
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

function recommend_reboot() {
    echo "[INFO] Now it's recommended to reboot your computer."
    read -r -p "[INFO] If you wish to automatically do that, just press enter. Otherwise, press CTRL+C"
    reboot 
}

check_root