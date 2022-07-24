# TCP redirector plugin (Redirectoooooor!)

With this plugin, you can connect to your Cellframe node UNIX socket remotely using my Cellframe node client: https://github.com/CELLgainz/Cellframe/tree/main/cellframe-node-client

Just place the folder to your plugins directory, restart your node and then use my client with:

	./cellframe-node-cli --ip <your_ip> --port <your_port>

Peace!

## Change configuration

You should also change some of the default configuration (eg. allowed IP addresses and the port). 

	port = 12345
	allowed = ["127.0.0.1", "localhost", "192.168.1.10"]

If you're connecting remotely to your node, you should get your public IP address and add it to that list. For example, if my external IP address is 88.34.53.1, just modify the list to:

	allowed = ["127.0.0.1", "localhost", "88.34.53.1"]

Please note that you can also remove all IP addresses completely to block all connections!