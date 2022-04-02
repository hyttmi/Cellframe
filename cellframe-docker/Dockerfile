FROM debian:bullseye-slim

# Basic settings for node
ARG SERVER_PORT=8079
ARG SERVER_ADDR=0.0.0.0
ARG DEBUG=false
ARG AUTO_ONLINE=true
ARG SERVER_ENABLED=true

# Network settings
ARG SUBZERO_ENABLED=true
ARG SUBZERO_NODE_TYPE=full
ARG CORE_T_ENABLED=false
ARG CORE_T_NODE_TYPE=full
ARG MINKOWSKI_ENABLED=true
ARG MINKOWSKI_NODE_TYPE=full
ARG KELVIN_ENABLED=true
ARG KELVIN_NODE_TYPE=full


ENV DEBIAN_FRONTEND noninteractive

ARG NODE_VERSION=5.0-55

ARG ARCH=amd64

ARG RUN_DEPS="libsqlite3-0 libjson-c5 libmagic1 inetutils-traceroute libpython3.9 wget debconf-utils dconf-cli less pv psmisc logrotate irqbalance xz-utils ca-certificates"

ARG RECOMMENDED="nano htop"

RUN apt-get update && apt-get -y dist-upgrade && apt-get -y install ${RUN_DEPS} && apt-get -y install ${RECOMMENDED}

RUN echo "cellframe-node cellframe-node/subzero_enabled select ${SUBZERO_ENABLED}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/server_addr	string	${SERVER_ADDR}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/auto_online	select	${AUTO_ONLINE}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/kelvpn_minkowski_node_type	select	${MINKOWSKI_NODE_TYPE}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/kelvin_testnet_enabled	select	${KELVIN_ENABLED}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/server_port	string	${SERVER_PORT}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/kelvin_testnet_node_type	select	${KELVIN_NODE_TYPE}" | debconf-set-selections  \
    && echo "cellframe-node cellframe-node/server_enabled	select	${SERVER_ENABLED}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/debug_mode	select	${DEBUG}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/core_t_node_type	select	${CORE_T_NODE_TYPE}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/kelvpn_minkowski_enabled	select	${MINKOWSKI_ENABLED}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/subzero_node_type	select	${SUBZERO_NODE_TYPE}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/core_t_enabled	select	${CORE_T_ENABLED}" | debconf-set-selections

RUN cd /tmp \
    && wget https://pub.cellframe.net/linux/cellframe-node-${NODE_VERSION}-${ARCH}.deb \
    && dpkg -i cellframe-node-${NODE_VERSION}-${ARCH}.deb

RUN apt-get -y autoremove --purge && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# We need to create a volume, otherwise the downloaded databases would be lost. 
VOLUME [ "/opt/cellframe-node" ]

COPY cellframe-node.sh /usr/bin/

RUN ln -sv /opt/cellframe-node/bin/cellframe* /usr/bin/

CMD [ "/usr/bin/cellframe-node.sh" ]
