#!/bin/bash

VERSION="0.1.9"

LOG="/tmp/CMI_v${VERSION}_$(date '+%d-%m-%Y-%T').log"

CELLFRAME_NODE_CLI_PATH="/opt/cellframe-node/bin/cellframe-node-cli"

check_root() {
    if [[ $EUID -ne 0 ]] ; then
        echo "--- Need root rights, exiting..."
        exit 1
    else
        showinfo
    fi
}

verify_node_running () {
    echo "--- Verifying that cellframe-node is running..." # Test that node is actually running and cli connects to socket.
    until run_cli version | grep -i 'cellframe-node version' > /dev/null
    do
        sleep 1
    done
}

run_cli() {
    /opt/cellframe-node/bin/cellframe-node-cli "$@"
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
    ##  setup it as a master node to your computer with as minimal        ##
    ##  as possible user input.                                           ##
    ##                                                                    ##
    ##  PREREQUISITES:                                                    ##
    ##                                                                    ##
    ##      1) Your public IP address (If script can't fetch it           ##
    ##         automatically)                                             ##
    ##                                                                    ##
    ##      2a) Seed phrase from your wallet (24 words)                   ##
    ##                                                                    ##
    ##            OR                                                      ##
    ##                                                                    ##
    ##      2b) .dwallet file (place to the same directory with           ##
    ##          the script)                                               ##
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
        check_node_presence
    else
        echo "--- Exiting..."
        exit 1
    fi
}

check_node_presence() {
    NODE_PATH="/opt/cellframe-node"
    [[ -d $NODE_PATH ]] &&  echo "--- Detected $NODE_PATH path, this script is meant for completely clean installs only. Exiting..." \
    && exit 1
    check_deps
}

check_deps() {
    echo "--- Checking necessary dependencies..."
    DEPS=(sed apt wget sha256sum wc)
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
    ARCH=$(dpkg --print-architecture)
    case "$ARCH" in \
      amd64) ARCH='amd64' && echo "--- Detected $ARCH architecture..." \
      && LATEST_VERSION=$(wget -qO- https://pub.cellframe.net/linux/cellframe-node/master/ | grep -oP "\Kcellframe-node-5.2.[0-9]{3}-updtr-amd64.deb" | sort | tail -n1) # Use the automatic updater version for amd64 architecture
      ;;
      arm64) ARCH='arm64' && echo "--- Detected $ARCH architecture..." \
      && LATEST_VERSION=$(wget -qO- https://pub.cellframe.net/linux/cellframe-node/master/ | grep -oP "\Kcellframe-node-5.2.[0-9]{3}-arm64.deb" | sort | tail -n1)
      ;;
      armhf) ARCH='armhf' && echo "--- Detected $ARCH architecture..." \
      && LATEST_VERSION=$(wget -qO- https://pub.cellframe.net/linux/cellframe-node/master/ | grep -oP "\Kcellframe-node-5.2.[0-9]{3}-armhf.deb" | sort | tail -n1)
      ;;
      *) echo "Unsupported architecture, exiting..." && exit 1
      ;;
    esac
    echo "--- Downloading latest version of Cellframe node..."
    wget -q https://pub.cellframe.net/linux/cellframe-node/master/$LATEST_VERSION
    echo "--- Installing $LATEST_VERSION..."
    DEBIAN_FRONTEND=noninteractive apt install -y -qq ./$LATEST_VERSION > /dev/null #stdout to nothingness!
    rm $LATEST_VERSION
    verify_node_running
    if [ -f $CELLFRAME_NODE_CLI_PATH ] && [ ! -x $CELLFRAME_NODE_CLI_PATH ]; then
        chmod +x $CELLFRAME_NODE_CLI_PATH #Make sure cli is executable
    fi
    create_cert
}


create_cert() {
    read -p "--- Input a desired name to your certificate: " cert
        if [[ $cert =~ ^[a-zA-Z0-9]*$ ]]; then
            echo "--- Your certificate backbone.$cert will be created..."
            /opt/cellframe-node/bin/cellframe-node-tool cert create backbone.$cert sig_dil
            declare -x -g CERT="backbone.$cert"
            check_wallet_files
        else
            echo "--- Supported characters are a-z, A-Z, 0-9. No spaces."
            create_cert
        fi
}

check_wallet_files() {
    SCRIPT_DIR=$(dirname "$0")
    WALLETPATH="/opt/cellframe-node/var/lib/wallet/"
    WALLETFILES=($(find $SCRIPT_DIR -iname '*.dwallet' -type f -printf '%f '))
    ARRAY_LEN=${#WALLETFILES[@]}
    if [[ ! -z $WALLETFILES ]]; then
        if [[ $ARRAY_LEN -gt 1 ]]; then
            echo "--- Found multiple wallets in current directory..."
            for i in ${!WALLETFILES[@]}
            do
                echo -e "\t==> [$i] -- ${WALLETFILES[$i]}"
            done
            read -p "--- Which one would you like to restore?: " number
            MAX_VALUE=$(($ARRAY_LEN - 1))
            if [[ $number =~ ^[0-9]$ && ! $number -gt $MAX_VALUE ]]; then 
                cp "$SCRIPT_DIR/${WALLETFILES[$number]}" $WALLETPATH
                echo "--- Wallet ${WALLETFILES[$number]} restored!"
                walletname="${WALLETFILES[$number]%.*}"
                declare -x -g WALLETNAME=$walletname
                echo "--- Restarting cellframe-node to load new wallet files..."
                systemctl restart cellframe-node.service
                verify_node_running
                declare -x -g WALLETADDRESS=$(run_cli wallet info -w $WALLETNAME -net Backbone | grep -oP 'addr: \K.*$')
                configure_node
            else
                echo "--- Not a valid number!"
                check_wallet_files
            fi
        else
            echo "--- Found .dwallet file current directory, copying to $WALLETPATH..."
            for i in ${WALLETFILES[@]}
            do
                walletname=$(basename "$i" .dwallet)
                declare -x -g WALLETNAME=$walletname
                cp "$SCRIPT_DIR/$i" $WALLETPATH
                echo "--- Restarting cellframe-node to load new wallet files..."
                systemctl restart cellframe-node.service
                verify_node_running
                declare -x -g WALLETADDRESS=$(run_cli wallet info -w $WALLETNAME -net Backbone | grep -oP 'addr: \K.*$')
                configure_node
            done
        fi
    else
        create_wallet
    fi
}

create_wallet() {
    read -p "--- Input a desired name to your wallet: " walletname
        if [[ $walletname =~ ^[a-zA-Z0-9]*$ ]]; then
            echo "--- Your wallet $walletname will be created..."
            declare -x -g WALLETNAME=$walletname
            get_seed
        else
            echo "--- Supported characters are a-z, A-Z, 0-9. No spaces."
            create_wallet
        fi
}

get_seed() {
    read -p "--- Input your 24 word seed phrase: " words
        count=$(echo $words | wc -w)
        if [[ $count -eq 24 ]]; then
            SHA256=$(echo -n $words | tr -d [:blank:] | sha256sum | cut -d " " -f1)
            echo "--- Your SHA256SUM of seed phrase is: $SHA256"
            run_cli wallet new -w $WALLETNAME -sign sig_dil -restore 0x$SHA256 -force | tee -a $LOG
            declare -x -g WALLETADDRESS=$(run_cli wallet info -w $WALLETNAME -net Backbone | grep -oP 'addr: \K.*$')
            configure_node
        else
            echo "--- Not a 24 word seed phrase, your seed phrase had $count words!"
            get_seed
        fi
}

configure_node() {
    NODE_CONFIG_FILE="/opt/cellframe-node/etc/cellframe-node.cfg"
    BACKBONE_CONFIG_FILE="/opt/cellframe-node/etc/network/Backbone.cfg"
    declare -x -g NODE_ADDR=$(run_cli net -net Backbone get status | grep -oP '[0-9A-Z]{4}::[0-9A-Z]{4}::[0-9A-Z]{4}::[0-9A-Z]{4}')
    [[ -z "${NODE_ADDR// }" ]] && echo "--- Can't get node address! Trying again..." && sleep 5 && configure_node || echo "--- Got node address: $NODE_ADDR"
    read -p "--- Input the amount of CELL tokens which will be automatically collected after a desired amount is accumulated: " collectamount
    if [[ $collectamount =~ ^[0-9]*$ ]]; then
        echo "--- Setting to $collectamount CELL tokens..."
    else
        echo "--- Unsupported value!"
        configure_node
    fi
    echo "--- Modifying node configuration..."
    sed -i "s/^auto_online=.*/auto_online=true/g" $NODE_CONFIG_FILE
    sed -i "0,/enabled=false/s//enabled=true/" $NODE_CONFIG_FILE
    sed -i "s/^auto_proc=.*/auto_proc=true/g"  $NODE_CONFIG_FILE
    echo "--- Modifying Backbone configuration..."
    sed -i "/^\[general\]/a node_addr_type=static" $BACKBONE_CONFIG_FILE
    sed -i "/^\[general\]/a node-addr=$NODE_ADDR" $BACKBONE_CONFIG_FILE
    sed -i "s/^node-role=.*/node-role=master/g"  $BACKBONE_CONFIG_FILE
    sed -i "s/^#blocks-sign-cert=.*/blocks-sign-cert=$CERT/g" $BACKBONE_CONFIG_FILE
    sed -i "s/^#fee_addr=.*/fee_addr=$WALLETADDRESS/g" $BACKBONE_CONFIG_FILE
    sed -i "/^\[esbocs\]/a set_collect_fee=$collectamount" $BACKBONE_CONFIG_FILE
    echo "--- Restarting cellframe-node, please wait..."
    systemctl restart cellframe-node.service
    verify_node_running
    create_validator_order
}

create_validator_order() {
    echo "--- Creating order for the validator fee... (using the recommended value of 0.05 \$CELL)"
    run_cli srv_stake order create -net Backbone -value 0.05e+18 -cert $CERT | tee -a $LOG
    get_public_ip
}

get_public_ip() {
    echo "--- Trying to get your current public IP address..."
    IP=$(wget -qO- api.ipify.org)
    [[ -z "${IP// }" ]] && echo "--- Can't get your public IP address, please input it manually!" && input_ip || declare -x -g IP=$IP && publish_node
}

input_ip() {
    read -p "--- Please input your IP address manually: " IP
    if [[ $IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        echo "--- Using $IP as your public IP address..."
        declare -x -g IP=$IP
        publish_node
    else
        echo "Not a valid IP address, please try again..."
        input_ip
    fi
}

publish_node() {
    read -p "--- Your current external IP address seems to be $IP. Does it look correct? (Y/N) " confirm
    if [[ $confirm =~ ^[yY]$ ]]; then
        echo "--- Publishing node...."
        run_cli node add -net Backbone -ipv4 $IP -port 8079 | tee -a $LOG
        if [[ $(cat $LOG | grep "Can't do handshake") ]]; then
            echo "--- Handshake failed to your node, are you behind a firewall/NAT? You may cancel with Ctrl+C"
            publish_node
        else
            echo "--- Adding diagnostics data file to /opt/cellframe-node/etc/diagdata.json..."
            echo "{\"name\":\"$NODE_ADDR\", \"category\":\"validator\", \"ip_addr\": \"$IP\"}" > /opt/cellframe-node/etc/diagdata.json
            check_wallet_balance
        fi
    else
        input_ip
    fi
}

check_wallet_balance() {
    echo "--- Checking your wallet balance..."
    BALANCE=$(run_cli wallet info -w $WALLETNAME -net Backbone | grep -oP '[0-9]*\.[0-9]+ \([0-9]*\) mCELL' | tr -d '()' | cut -d ' ' -f 1 | wc -m)
    if [[ $BALANCE -lt 21 ]]; then
        echo "--- Looks like you don't have enough mCELL on your wallet. It's possible that cellframe-node is still syncing wallet data. Will wait for 1 hour (cancel with CTRL+C)..."
        sleep 1h
        check_wallet_balance
    else
        lock_mcell
    fi
}


lock_mcell() {
    BALANCE=$(run_cli wallet info -w $WALLETNAME -net Backbone | grep -oP '[0-9]*\.[0-9]+ \([0-9]*\) mCELL' | tr -d '()' | cut -d ' ' -f 1)
    echo "--- Your current wallet balance is $BALANCE"
    read -p "Enter the amount which you want to lock for your mastenode (no decimals): " MCELL
    if [[ ! $MCELL =~ ^[0-9]*$ && $MCELL -lt 10 ]]; then
        echo "--- Invalid amount of tokens! Please try again..."
        lock_mcell
    else
        echo "--- Delegating stake..."
        run_cli srv_stake delegate -cert $CERT -net Backbone -w $WALLETNAME -value $MCELL.0e+18 -node_addr $NODE_ADDR -fee 0.05e+18 | tee -a $LOG
        msg_ready
    fi
}

msg_ready() {
    echo "--- Everything done, please post your stake transaction hash to the Cellframe Support Telegram group"
    read -p "Do you want to view the log file? (Y/N) " confirm
    if [[ $confirm =~ ^[yY]$ ]]; then
        cat $LOG
    else
        exit
    fi
}

check_root