FROM debian:stable-slim

# Basic settings for node
ARG SERVER_PORT="8079"
ARG SERVER_ADDR="0.0.0.0"
ARG DEBUG="false"
ARG AUTO_ONLINE="true"
ARG SERVER_ENABLED="true"
ARG NOTIFY_SRV_ADDR="127.0.0.1"
ARG NOTIFY_SRV_PORT="8080"
ARG ENABLE_PYTHON_PLUGINS="true"
ARG PYTHON_PLUGINS_PATH="/home/cellframe/plugins"

# Network settings
ARG BACKBONE_ENABLED="true"
ARG BACKBONE_NODE_TYPE="master"
ARG MILEENA_ENABLED="true"
ARG MILEENA_NODE_TYPE="full"
ARG MINKOWSKI_ENABLED="true"
ARG MINKOWSKI_NODE_TYPE="full"
ARG SUBZERO_ENABLED="true"
ARG SUBZERO_NODE_TYPE="full"

ENV DEBIAN_FRONTEND noninteractive

ARG RUN_DEPS="libsqlite3-0 libjson-c5 libmagic1 inetutils-traceroute libpython3.9 debconf-utils curl dconf-cli less pv psmisc logrotate irqbalance xz-utils ca-certificates"

RUN apt-get update && apt-get -y dist-upgrade && apt-get -y install ${RUN_DEPS}

RUN echo "cellframe-node cellframe-node/mileena_enabled	select ${MILEENA_ENABLED}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/mileena_node_type select ${$MILEENA_NODE_TYPE}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/kelvpn_minkowski_enabled select ${MINKOWSKI_ENABLED}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/kelvpn_minkowski_node_type select ${MINKOWSKI_NODE_TYPE}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/backbone_enabled select ${BACKBONE_ENABLED}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/backbone_node_type select ${BACKBONE_NODE_TYPE}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/subzero_enabled select ${SUBZERO_ENABLED}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/subzero_node_type select ${SUBZERO_NODE_TYPE}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/notify_srv_port string ${NOTIFY_SRV_PORT}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/notify_srv_addr string ${NOTIFY_SRV_ADDR}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/auto_online select ${AUTO_ONLINE}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/server_enabled select ${SERVER_ENABLED}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/debug_mode select ${DEBUG}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/python_plugins_path string ${PYTHON_PLUGINS_PATH}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/enable_python_plugins select ${ENABLE_PYTHON_PLUGINS}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/server_port string ${SERVER_PORT}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/server_addr string ${SERVER_ADDR}" | debconf-set-selections

RUN cd /tmp \
    && NODE_VERSION=`curl -v --silent https://pub.cellframe.net/linux/ 2>&1 | grep -oP ">cellframe-node-\K5.1.[0-9]{3}" | sort | tail -n1` \
    && ARCH=`dpkg --print-architecture` \
    && case "${ARCH}" in \
      amd64) ARCH='amd64';; \
      arm64) ARCH='arm64';; \
      armhf) ARCH='armhf';; \
      *) echo "Unsupported architecture, exiting..."; exit 1 ;; \
    esac \
    && curl -O https://pub.cellframe.net/linux/cellframe-node-${NODE_VERSION}-${ARCH}.deb \
    && dpkg -i cellframe-node-${NODE_VERSION}-${ARCH}.deb

RUN apt-get -y autoremove --purge && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /home/cellframe/gdb \
&& mkdir -p /home/cellframe/wallet \
&& mkdir -p /home/cellframe/plugins

# We need to create a volume, otherwise the downloaded databases would be lost. 
VOLUME [ "/home/cellframe" ]

COPY cellframe-node.sh /usr/bin/

RUN chmod 777 /usr/bin/cellframe-node.sh

CMD [ "/usr/bin/cellframe-node.sh" ]
