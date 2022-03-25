## Cellframe node installer script

This is as simple as it can possibly get. Tested only on Debian, might work on Ubuntu too.

For aarch64 (Raspberry Pi 3/4/400) and x86_64.

Should take care of all dependencies, please report if it doesn't.

It adds Demlabs public key/repository and then installs the latest version of Cellframe node.

If you don't have wget installed, get the script with curl:

    curl -O https://raw.githubusercontent.com/CELLgainz/Cellframe/main/cellframe-installer/cellframe-installer.sh

Or if you have wget installed, use:

    wget https://raw.githubusercontent.com/CELLgainz/Cellframe/main/cellframe-installer/cellframe-installer.sh

After downloading:

    chmod +x cellframe-installer.sh

After that, run with:

    ./cellframe-installer (as root/sudo)

Done!
