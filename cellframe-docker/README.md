# Dockerfile for building your own Docker image

With this Dockerfile you can build your own Cellframe node docker image from the latest node version available.

Docker file has a few ARGs which can be changed:

```sh
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

# Architecture
ARG ARCH="amd64"
```

These args are passed to debconf-set-selections before node installation.

## Build the image yourself

1. First, create an image by executing the following command from the current directory:

    ```sh
    docker build -t <name> .
    ```

    ❗️ If you are on a **Mac with Apple Silicon**, execute the following command instead:

     ```sh
    docker build -t <name> --build-arg ARCH=arm64 .
    ```

2. Then create a volume with:

    ```sh
    docker volume create cellframe
    ```

3. And start the node by running:

    ```sh
    docker run -v cellframe:/home/cellframe --name=cellframe-node --privileged --net=host -it <name>
    ```

4. Or as daemon:

    ```sh
    docker run -v cellframe:/home/cellframe --name=cellframe-node --privileged --net=host -it -d <name>
    ```

5. If running as daemon, check the logs with

   ```sh
   docker logs -f cellframe-node
   ```

## Change settings via environment variables

I added support for changing few settings via environment variables before launching the node. Variables are:

```sh
SERVER_PORT    # defaults to 8079
SERVER_ADDR    # defaults to 0.0.0.0
DEBUG          # defaults to false
AUTO_ONLINE    # defaults to true
SERVER_ENABLED # defaults to true
```

So for example, before launching the node you can set the variable for SERVER_PORT:

```sh
docker run -e SERVER_PORT=6666 -v cellframe:/home/cellframe --name=cellframe-node  --privileged--net=host <name>
```

Beware though, there is no proper check for IP address for example.
