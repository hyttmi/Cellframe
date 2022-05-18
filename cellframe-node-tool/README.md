## Cellframe node tool

With this tool, you can install latest Cellframe node, completely uninstall installed Cellframe node (script automatically does a backup of your wallet) or do some basic troubleshooting if your node is not working for some reason.

For installation aarch64 and x86_64 are supported.

Should support every Debian based linux distro there is.

If you don't have wget installed by default, get the script with curl:

    curl -O https://raw.githubusercontent.com/CELLgainz/Cellframe/main/cellframe-installer/cellframe-node-tool.sh

Or if you have wget installed, use:

    wget https://raw.githubusercontent.com/CELLgainz/Cellframe/main/cellframe-installer/cellframe-node-tool.sh

After downloading:

    chmod +x cellframe-node-tool.sh

After that, run with:

    ./cellframe-node-tool.sh (as root)

Done!

## Some notes

There are no special checks to test if everything is working, the script expects that you have internet connection ready etc. If it doesn't work, please DM me on Telegram or in Twitter @CELLgainz
