ARG AUTO_ONLINE="true"
ARG SERVER_ENABLED="true" 

FROM debian:12

ENV DEBIAN_FRONTEND noninteractive

RUN apt update && apt -y dist-upgrade && apt -y install wget libexpat1 libmagic1

RUN echo "cellframe-node cellframe-node/auto_online select ${AUTO_ONLINE}" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/server_enabled select ${SERVER_ENABLED}" | debconf-set-selections

RUN cd /tmp \
    && LATEST_VERSION=$(wget -qO- https://pub.cellframe.net/linux/cellframe-node/master/ | grep -oP "\Kcellframe-node-5.2.[0-9]{3}-amd64.deb" | sort | tail -n1) \
    && ARCH=$(dpkg --print-architecture) \
    && case "${ARCH}" in \
      amd64) ARCH='amd64';; \
      arm64) ARCH='arm64';; \
      armhf) ARCH='armhf';; \
      *) echo "Unsupported architecture, exiting..."; exit 1 ;; \
    esac \
    && wget -q https://pub.cellframe.net/linux/cellframe-node/master/${LATEST_VERSION} \
    && apt install -y ./${LATEST_VERSION} \
    && rm $LATEST_VERSION

RUN apt -y autoremove --purge && apt clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN /opt/cellframe-node/bin/cellframe-node
