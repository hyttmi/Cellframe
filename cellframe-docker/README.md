# Dockerfile for building your own Cellframe Node Docker image

With this Dockerfile you can build your own Cellframe node docker image from the latest node version available.

## Build the image yourself

1. First, create an image by executing the following command from the current directory:

    ```sh
    docker build -t <name> .
    ```

2. Then create a volume with:

    ```sh
    docker volume create cellframe
    ```

3. And start the node by running:

    ```sh
    docker run -v cellframe:/opt/cellframe-node --name=cellframe-node --privileged --net=host -it <name>
    ```

4. Or as daemon:

    ```sh
    docker run -v cellframe:/opt/cellframe-node --name=cellframe-node --privileged --net=host -it -d <name>
    ```

5. If running as daemon, check the logs with

   ```sh
   docker logs -f cellframe-node
   ```