# Cellframe node client for interacting with your node via provided UNIX socket

With this tool, you can connect to your Cellframe node locally using UNIX socket (which Cellframe node conveniently supports)
or you can connect to your node from everywhere if you have forwarded UNIX socket with socat.

## Forwarding the UNIX socket

Make sure you have `socat` utility installed to your distribution. For Debian and it's derivatives:

    ```sh
    sudo apt install socat
    ```
For other distros, please search `socat` from repositories.

After installation, execute it with:

    ```sh
    socat TCP-LISTEN:12345,reuseaddr,fork UNIX-CLIENT:/opt/cellframe-node/var/run/node_cli &
    ```

Where 12345 can be changed to a port which you would like to use.

## Using the client

By default, the client uses local socket connection to your node. If you want to remotely connect to your node, you have to first forward your UNIX socket with socat
as explained above.

For local socket connection, just execute:

    ```sh
    ./cellframe-node-cli
    ```

And for remote connections:

    ```sh
    ./cellframe-node-cli --ip <ip_address> --port <port>
    ```

Where IP address is the hosts external IP address and port is the socat forwarded port.