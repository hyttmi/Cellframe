#!/bin/bash

DEPS="wget gnupg libpython3.9 libmagic1"
ARCH=`uname -m`
CODENAME=`lsb_release -cs`

if  [[ ! $(which lsb_release) ]] ; then
    echo "lsb_release not found. Install it with apt install lsb-release"
    exit
else
    echo "lsb_release found. Continuing..."
fi

if [[ $EUID -ne 0 ]] ; then
   echo "This script must be run as root." 
   exit 1
fi

if [[ ${ARCH} == "x86_64" || ${ARCH} == "aarch64" ]] ; then
    echo "${ARCH} is supported. Continuing... "
else
    echo "${ARCH} is not supported. Exiting..."
    exit 1
fi

if [[ ${CODENAME} == "bullseye" || ${CODENAME} == "focal" ]] ; then
    echo "Your distro is supported. Continuing..."
else 
    echo "Your distro is not supported, exiting..."
    exit 1 
fi

if [[ ${ARCH} == "aarch64" && ${CODENAME} != "bullseye" ]] ; then
    echo "Detected arm64 platform but there's no package for your distro @ Demlabs repository. Exiting..."
    exit 1
fi

echo "You have now 10 seconds before this script continues, cancel by pressing Ctrl+C"
sleep 10
echo "Setting up Demlabs public key..."
wget -q -O- https://debian.pub.demlabs.net/public/public-key.gpg | gpg --dearmor | tee /usr/share/keyrings/demlabs-archive-keyring.gpg > /dev/null
echo "Adding Demlabs repository to known sources..."
echo "deb [signed-by=/usr/share/keyrings/demlabs-archive-keyring.gpg] https://debian.pub.demlabs.net/public ${CODENAME} main" > /etc/apt/sources.list.d/demlabs.list
echo "Upgrading your installation and installing dependencies, this might take a while..."
apt-get -qq update && apt-get -yqq install ${DEPS} && apt-get -yqq dist-upgrade
echo "Cellframe node installation starts in 10 seconds. You need to answer couple of questions during installation."
sleep 10
echo "Installing Cellframe node"
apt-get -qq update && apt-get -yqq install cellframe-node

echo "All done! Script will automatically reboot your system in 10 seconds, you can cancel this by pressing Ctrl+C"
sleep 10
reboot
