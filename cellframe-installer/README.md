## Cellframe node installer script

This is as simple as it can possibly get. Tested on Ubuntu too.

For aarch64 and x86_64.

Should support every Debian based linux distro there is.

It adds Demlabs public key/repository if your platform is supported and then installs the latest version of Cellframe node.
Otherwise it downloads it straight from repository without adding it to sources.

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
