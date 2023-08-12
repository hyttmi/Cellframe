FROM ubuntu:latest

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -y dist-upgrade && apt-get -y install wget libexpat1 libmagic1

RUN echo "cellframe-node cellframe-node/auto_online select true" | debconf-set-selections \
    && echo "cellframe-node cellframe-node/server_enabled select true" | debconf-set-selections

RUN cd /tmp \
    && ARCH=$(dpkg --print-architecture) \
    && case "${ARCH}" in \
      amd64) ARCH='amd64';; \
      arm64) ARCH='arm64';; \
      armhf) ARCH='armhf';; \
      *) echo "Unsupported architecture, exiting..."; exit 1 ;; \
      esac \
    && LATEST_VERSION=$(wget -qO- https://pub.cellframe.net/linux/cellframe-node/master/ | grep -oP "\Kcellframe-node-5.2.[0-9]{3}-${ARCH}.deb" | sort | tail -n1) \
    && wget https://pub.cellframe.net/linux/cellframe-node/master/${LATEST_VERSION} \
    && apt -y install ./${LATEST_VERSION} \
    && rm $LATEST_VERSION

VOLUME ["/opt/cellframe-node"]

RUN apt-get -y autoremove --purge && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD /opt/cellframe-node/bin/cellframe-node
