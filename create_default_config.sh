#!/bin/bash
DAP_APP_NAME="cellframe-node"
DAP_PREFIX="/opt/$DAP_APP_NAME"

DAP_CFG_TPL="$DAP_PREFIX/share/configs/$DAP_APP_NAME.cfg.tpl"
DAP_CFG="$DAP_PREFIX/etc/$DAP_APP_NAME.cfg"

NETS=( Backbone subzero kelvpn-minkowski mileena )
NODE_ROLE="full"

AUTO_ONLINE="true"
SERVER_ENABLED="true"
SERVER_ADDR="0.0.0.0"
SERVER_PORT="8079"
NOTIFY_ADDR="127.0.0.1"
NOTIFY_PORT="8080"
DEBUG_MODE="false"


# 1. Configure networks

for NET_NAME in "${NETS[@]}"
do
    DAP_CFG_NET="$DAP_PREFIX/etc/network/$NET_NAME.cfg"
    DAP_CFG_NET_TPL="$DAP_PREFIX/share/configs/network/$NET_NAME.cfg.tpl"
    cat $DAP_CFG_NET_TPL > $DAP_CFG_NET
    sed -i "s|{NODE_TYPE}|$NODE_ROLE|g" $DAP_CFG_NET
done

# 2. Configure cellframe-node

cat $DAP_CFG_TPL > $DAP_CFG
sed -i "s|{PREFIX}|$DAP_PREFIX|g" $DAP_CFG
sed -i "s|{DEBUG_MODE}|$DEBUG_MODE|g" $DAP_CFG
sed -i "s|{AUTO_ONLINE}|$AUTO_ONLINE|g" $DAP_CFG
sed -i "s|{SERVER_ENABLED}|$SERVER_ENABLED|g" $DAP_CFG
sed -i "s|{SERVER_PORT}|$SERVER_PORT|g" $DAP_CFG
sed -i "s|{SERVER_ADDR}|$SERVER_ADDR|g" $DAP_CFG
sed -i "s|{NOTIFY_SRV_ADDR}|$NOTIFY_ADDR|g" $DAP_CFG
sed -i "s|{NOTIFY_SRV_PORT}|$NOTIFY_PORT|g" $DAP_CFG

ln -sf $DAP_PREFIX/share/$DAP_APP_NAME.service /etc/systemd/system/$DAP_APP_NAME.service
ln -sf ${DAP_PREFIX}/share/logrotate/${DAP_APP_NAME} /etc/logrotate.d/${DAP_APP_NAME}
mkdir -p ${DAP_PREFIX}/var/{run,lib/wallet,lib/global_db,lib/plugins,log}
systemctl enable --now ${DAP_PREFIX}/share/${DAP_APP_NAME}.service
