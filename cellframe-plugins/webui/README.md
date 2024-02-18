# Cellframe (master)node WebUI

With this plugin, it's easy to check your node autocollect stats and some other things too. 100% themeable!

## Installation

1. Enable Python plugins in `cellframe-node.cfg`.
2. Place the `webui` directory to `/opt/cellframe-node/var/lib/plugins/` (If it doesn't exist, create it).
3. Go to `/opt/cellframe-node/python/bin` and make sure pip/pip3 is executable `(chmod +x pip pip3)`
4. Go back to `/opt/cellframe-node/var/lib/plugins/webui` and install required packages with `/opt/cellframe-node/python/bin/pip3 requirements.txt`
5. OPTIONAL: Edit `webui.py` file `ALLOWED_IP_RANGES = ["0.0.0.0/0"]`, by default, you can access from any IP. (You can use multiple IP ranges)
6. OPTIONAL: Add new section to `cellframe-node.cfg` for setting basic authentication
   ```
   [webui]
   port=9999 # this can be any port you want, not mandatory though
   username=username
   password=password
   ```
7. Restart your node and access the WebUI with your browser.

## Themes
TODO