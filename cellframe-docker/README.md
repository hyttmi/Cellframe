# Dockerfile for building your own Docker image
With this Dockerfile you can build your own Cellframe node docker image.

Docker file has a few ARGs which can be changed:

    # Basic settings for node
    ARG SERVER_PORT="8079"
    ARG SERVER_ADDR="0.0.0.0"
    ARG DEBUG="false"
    ARG AUTO_ONLINE="true"
    ARG SERVER_ENABLED="true"
    ARG NOTIFY_SRV_ADDR="127.0.0.1"
    ARG NOTIFY_SRV_PORT="8080"
    ARG ENABLE_PYTHON_PLUGINS="false"
    ARG PYTHON_PLUGINS_PATH="/opt/cellframe-node/var/lib/plugins"

    # Network settings
    ARG BACKBONE_ENABLED="true"
    ARG BACKBONE_NODE_TYPE="full"
    ARG MILEENA_ENABLED="true"
    ARG MILEENA_NODE_TYPE="full"
    ARG MINKOWSKI_ENABLED="true"
    ARG MINKOWSKI_NODE_TYPE="full"
    ARG SUBZERO_ENABLED="true"
    ARG SUBZERO_NODE_TYPE="full"

These args are passed to debconf-set-selections before node installation.

## Build the image yourself
1. Just launch from the command line the following command:
    ```
    docker build -t <name> Dockerfile
    ```
2. Then create a volume with:
    ```
    docker volume create cellframe
    ```

3. And start the node by running:
    ```
    docker run -v cellframe:/home/cellframe --name=cellframe-node --privileged --net=host -it <name>
    ```

4. Or as daemon:
    ```
    docker run -v cellframe:/home/cellframe --name=cellframe-node --privileged --net=host -it -d <name>
    ```

5. If running as daemon, check the logs with
   ```
   docker logs -f cellframe-node
   ```

## Change settings via environment variables
I added support for changing few settings via environment variables before launching the node. Variables are:
    
    SERVER_PORT (default 8079)
    SERVER_ADDR (default 0.0.0.0)
    DEBUG (default false)
    AUTO_ONLINE (default true)
    SERVER_ENABLED (default true)

So for example, before launching the node you can set the variable for SERVER_PORT:
    ```
    docker run -e SERVER_PORT=6666 -v cellframe:/home/cellframe --name=cellframe-node  --privileged--net=host <name>
    ```

Beware though, there is no proper check for IP address for example.