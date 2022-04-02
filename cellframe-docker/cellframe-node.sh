#!/bin/bash

if  [[ $SERVER_PORT && $SERVER_PORT < 1 || $SERVER_PORT > 65535 ]] ; then
    echo "Listen port set to ${SERVER_PORT}"
    sed -i "s/^listen_port_tcp=.*/listen_port_tcp=${SERVER_PORT}/" $CONFIG
fi

if [[ $SERVER_ADDR && $SERVER_ADDR =~ ^(([1-9]?[0-9]|1[0-9][0-9]|2([0-4][0-9]|5[0-5]))\.){3}([1-9]?[0-9]|1[0-9][0-9]|2([0-4][0-9]|5[0-5]))$ ]] ; then
    echo "Server address set to ${SERVER_ADDR}"
    sed -i "s/^listen_address=.*/listen_address=${SERVER_ADDR}/" $CONFIG
fi

if [[ $AUTO_ONLINE && $AUTO_ONLINE == "true" || $AUTO_ONLINE == "false" ]] ; then
    echo "Auto online mode set to ${AUTO_ONLINE}"
    sed -i "s/^auto_online=.*/auto_online=${AUTO_ONLINE}/" $CONFIG
fi

if [[ $SERVER_ENABLED && $SERVER_ENABLED == "true" || $SERVER_ENABLED == "false" ]] ; then
    echo "Server enabled set to ${SERVER_ENABLED}"
    sed -i "0,/enabled=.*/s//enabled=${SERVER_ENABLED}/" $CONFIG
fi

/usr/bin/cellframe-node
