#!/bin/bash

LOG="/tmp/CMI.log"

check_root() {
    if [[ $EUID -ne 0 ]] ; then
        echo "Need root rights, exiting..."
        exit 1
    else
        showinfo
    fi
}

showinfo() {
    cat << EOF

    ########################################################################
    ########################################################################
    ##                                                                    ##
    ##  Cellframe Masternode Installer // CMI                             ##
    ##  __________________________________________                        ##
    ##                                                                    ##
    ##  Welcome to Cellframe Mastenode installation script.               ##
    ##                                                                    ##
    ##  This script tries to install the latest Cellframe Node and        ##
    ##  setup it as a master node to your computer with minimal           ##
    ##  as possible user input.                                           ##
    ##                                                                    ##
    ##  PREREQUISITES:                                                    ##
    ##                                                                    ##
    ##      1.) Seed phrase from your wallet (24 words)                   ##
    ##                                                                    ##
    ##  Problems may occur and therefore the creator of this script       ##
    ##  won't be responsible about any lost funds or wallets if/when      ##
    ##  using this script!                                                ##
    ##                                                                    ##
    ##  Issues with the script? Ping @CELLgainz in Telegram :)            ##
    ##                                                                    ##
    ########################################################################
    ########################################################################
EOF
    read -p "Are you sure you want to continue? (Y/N) " confirm
    if [[ $confirm =~ ^[yY]$ ]]; then
        clear
        echo "--- Continuing in 5 seconds, you may still exit with CTRL+C..."
        echo "--- Logging to $LOG"
        sleep 5
        check_deps
    else
        echo "--- Exiting..."
        exit 1
    fi
}

check_deps() {
    echo "--- Checking necessary dependencies..."
    DEPS=(sed apt wget)
    for i in ${DEPS[@]}
    do
        if [[ $(command -v $i) ]]; then
            echo -e "\t==> $i found, continuing..."
        else
            echo -e "\t==> $i not found, exiting..."
            exit 1
        fi
    done
    download_and_install_node
}

download_and_install_node() {
    echo "--- Downloading latest version of Cellframe node..."
    LATEST_VERSION=$(wget -qO- https://pub.cellframe.net/linux/cellframe-node/master/ | grep -oP "\Kcellframe-node-5.2.[0-9]{3}-updtr-amd64.deb" | sort | tail -n1)
    wget https://pub.cellframe.net/linux/cellframe-node/master/$LATEST_VERSION
    DEBIAN_FRONTEND=noninteractive apt install -y -qq ./$LATEST_VERSION > /dev/null #stdout to nothingness!
    rm $LATEST_VERSION
    create_cert
}

create_cert() {
    read -p "--- Input a desired name to your certificate: " cert
        if [[ $cert =~ ^[a-zA-Z0-9]*$ ]]; then
            echo "--- Your certificate backbone.$cert will be created..."
            sh -c "/opt/cellframe-node/bin/cellframe-node-tool cert create backbone.$cert sig_dil"
            declare -x -g CERT="backbone.$cert"
            create_wallet
        else
            echo "--- Supported characters are a-z, A-Z, 0-9."
            create_cert
        fi
}

create_wallet() {
    read -p "--- Input a desired name to your wallet: " walletname
        if [[ $walletname =~ ^[a-zA-Z0-9]*$ ]]; then
            echo "--- Your wallet $walletname will be created..."
            declare -x -g WALLETNAME=$walletname
            get_seed
        else
            echo "--- Supported characters are a-z, A-Z, 0-9."
            create_wallet
        fi
}
get_seed() {
    read -p "--- Input your 24 word seed phrase: " words
        count=$(echo $words | wc -w)
        if [[ $count -eq 24 ]]; then
            SHA256=$(echo -n $words | tr -d [:blank:] | sha256sum | cut -d " " -f1)
            echo "--- Your SHA256SUM of seed phrase is: $SHA256"
            sh -c "/opt/cellframe-node/bin/cellframe-node-cli wallet new -w $WALLETNAME -sign sig_dil -restore 0x$SHA256 -force | tee -a $LOG"
            declare -x -g WALLETADDRESS=$(sh -c "/opt/cellframe-node/bin/cellframe-node-cli wallet info -w $WALLETNAME -net Backbone | grep -oP 'addr: \K.*$'")
            configure_node
        else
            echo "--- Not a 24 word seed phrase, your seed phrase had $count words!"
            get_seed
        fi
}

configure_node() {
    NODE_CONFIG_FILE="/opt/cellframe-node/etc/cellframe-node.cfg"
    BACKBONE_CONFIG_FILE="/opt/cellframe-node/etc/network/Backbone.cfg"
    NODE_ADDR=$(sh -c "/opt/cellframe-node/bin/cellframe-node-cli net -net Backbone get status | grep -oP '[0-9A-Z]{4}::[0-9A-Z]{4}::[0-9A-Z]{4}::[0-9A-Z]{4}'")
    echo "--- Modifying node configuration..."
    sed -i "s/^auto_online=.*/auto_online=true/g" $NODE_CONFIG_FILE
    sed -i "0,/enabled=false/s//enabled=true/" $NODE_CONFIG_FILE
    sed -i "s/^auto_proc=.*/auto_proc=true/g"  $NODE_CONFIG_FILE
    sed -i "/^\[general\]/a node_addr_type=static" $NODE_CONFIG_FILE
    sed -i "/^\[general\]/a node-addr=$NODE_ADDR" $NODE_CONFIG_FILE
    echo "--- Modifying Backbone configuration..."
    sed -i "s/^node-role=.*/node-role=master/g"  $BACKBONE_CONFIG_FILE
    sed -i "s/^#blocks-sign-cert=.*/blocks-sign-cert=$CERT/g" $BACKBONE_CONFIG_FILE
    sed -i "s/^#fee_addr=.*/fee_addr=$WALLETADDRESS/g" $BACKBONE_CONFIG_FILE
    read -p "--- Input the amount of CELL tokens which will be automatically collected after a desired amount is accumulated: " collectamount
    if [[ $collectamount =~ ^[0-9]*$ ]]; then
        echo "--- Setting to $collectamount of CELL tokens..."
    else
        echo "--- Unsupported value, using default value of 2 CELL tokens"
        collectamount=2
    fi
    sed -i "/^\[esbocs\]/a set_collect_fee=$collectamount" $BACKBONE_CONFIG_FILE
}

check_root