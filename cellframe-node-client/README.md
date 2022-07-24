# Cellframe node client for interacting with your node via provided UNIX socket

With this tool, you can connect to your Cellframe node locally using UNIX socket (which Cellframe node conveniently supports)
or you can connect to your node from everywhere if you have forwarded UNIX socket with socat or with my redirectoooooor plugin.

## Forwarding the UNIX socket

Make sure you have `socat` utility installed to your distribution. For Debian and it's derivatives:

    sudo apt install socat

For other distros, please search `socat` from repositories.

After installation, execute it with:

    socat TCP-LISTEN:12345,reuseaddr,fork UNIX-CLIENT:/opt/cellframe-node/var/run/node_cli &

Where 12345 can be changed to a port which you would like to use.

## Using my redirectoooooor plugin

I have created a handy plugin for Cellframe node which creates an external socket and then redirects the data to the Cellframe node UNIX socket. Just place it in your plugins folder, change the port (and possibly modify the allowed IP address list) and off you go!

You can find the plugin here: https://github.com/CELLgainz/Cellframe/tree/main/cellframe-plugins/redirectoooooor

## Using the client

By default, the client uses local socket connection to your node. If you want to remotely connect to your node, you have to first forward your UNIX socket with socat
as explained above.

For local socket connection, just execute:


    ./cellframe-node-cli


And for remote connections:


    ./cellframe-node-cli --ip <ip_address> --port <port>


Where IP address is the hosts external IP address and port is the socat forwarded port.