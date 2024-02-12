# Cellframe (master)node WebUI

With this plugin, it's easy to check your node autocollect stats and some other things too.

## Installation

1. Enable Python plugins in `cellframe-node.cfg`.
2. Place the `webui` directory to `/opt/cellframe-node/var/lib/plugins/` (If it doesn't exist, create it).
3. Edit `webui.py` file `ALLOWED_IP_RANGES = ["0.0.0.0/0"]`, by default, you can access from any IP. (You can use multiple IP ranges)
4. Edit `webui.py` file `PORT = 9999` to a port which you want to use.
5. Restart your node and access the WebUI with your browser.