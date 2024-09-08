# Cellframe (master)node WebUI

With this plugin, it's easy to check your node autocollect stats and some other things too. 100% themeable!

## Installation

1. Enable Python plugins in `cellframe-node.cfg`.
2. Place the `webui` directory to `/opt/cellframe-node/var/lib/plugins/` (If it doesn't exist, create it).
3. Go to `/opt/cellframe-node/python/bin` and make sure pip/pip3 is executable `(chmod +x pip pip3)`
4. Go back to `/opt/cellframe-node/var/lib/plugins/webui` and install required packages with `/opt/cellframe-node/python/bin/pip3 install -r requirements.txt` **AS ROOT**
5. Restart your node and access the WebUI with your browser.

## Configuration

Configuration of the plugin is done by editing `cellframe-node.cfg` file in `/opt/cellframe-node/etc/cellframe-node.cfg`. You just need to add new section `[webui]` to the end of the file and below that, add the settings which you want to change:

- `username=john` - Sets http authentication as user john. **MANDATORY**
- `password=p4a55w0rd` - Sets password to p4a55w0rd. **MANDATORY**
- `template=something` - Change template to something. If not set, default template will be used (cards).
