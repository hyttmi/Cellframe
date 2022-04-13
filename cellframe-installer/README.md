## Cellframe node installer script

This is as simple as it can possibly get. Tested on Ubuntu too.

Supports ONLY Debian 11 and Ubuntu 20.04.x (now also Linux Mint elsie, which is bullseye).

For aarch64 (Raspberry Pi 3/4/400) and x86_64.

Should take care of all dependencies, which are sometimes missing from default Debian/Ubuntu installation.

It adds Demlabs public key/repository and then installs the latest version of Cellframe node.

If you don't have wget installed by default, get the script with curl:

    curl -O https://raw.githubusercontent.com/CELLgainz/Cellframe/main/cellframe-installer/cellframe-installer.sh

Or if you have wget installed, use:

    wget https://raw.githubusercontent.com/CELLgainz/Cellframe/main/cellframe-installer/cellframe-installer.sh

After downloading:

    chmod +x cellframe-installer.sh

After that, run with:

    ./cellframe-installer.sh (as root)

Done!

## Some notes

There are no special checks to test if everything is working, the script expects that you have internet connection ready etc. If it doesn't work, please DM me on Telegram or in Twitter @CELLgainz
