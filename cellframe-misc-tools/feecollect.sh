#!/bin/bash

CERT="<your_certificate_name>"
WALLET_ADDR="<your_wallet_address>"
HASHES=$(sh -c "/opt/cellframe-node/bin/cellframe-node-cli block list -net Backbone -chain main -cert $CERT -unspent | grep -oP '0x.{64}' | tr '\n' ','")


if [[ -z $HASHES ]]; then
    echo "Can't get any hashes, is cellframe-node running?"
else
    sh -c "/opt/cellframe-node/bin/cellframe-node-cli block fee collect -cert $CERT -addr $WALLET_ADDR -net Backbone -chain main -hashes $HASHES -fee 0.05e+18"
fi


