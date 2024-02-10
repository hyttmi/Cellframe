# Node stats plugin for Cellframe node
1. Create path for plugin: `mkdir -p /opt/cellframe-node/var/lib/plugins/node_stats`
2. Download `manifest.json`and `node_stats.py` to that path
3. Enable Python plugins in `cellframe-node.cfg`
4. Edit `PORT`and `ALLOWED_IP_RANGES`in `node_stats.py`
5. Run node!