#!/bin/bash

VERSION="0.2.0"
LOG="/tmp/CMI_v${VERSION}_$(date '+%d-%m-%Y-%T').log"

CELLFRAME_NODE_CLI_PATH="/opt/cellframe-node/bin/cellframe-node-cli"
CELLFRAME_NODE_CONFIG_PATH="/opt/cellframe-node/bin/cellframe-node-config"
CELLFRAME_NODE_TOOL_PATH="/opt/cellframe-node/bin/cellframe-node-tool"

declare -A token_array=(
    [Backbone]='CELL'
    [KelVPN]='KEL'
    [raiden]='tCELL'
    [riemann]='tKEL'
)

declare -A mtoken_array=(
    [Backbone]='mCELL'
    [KelVPN]='mKEL'
    [raiden]='mtCELL'
    [riemann]='mtKEL'
)

declare -A fee_order_array=(
    [Backbone]='0.01'
    [KelVPN]='1.0'
    [raiden]='0.05'
    [riemann]='0.05'
)

Help()
{

cat << EOF

    Welcome to Cellframe Mastenode installation script.  

    This script will install Cellframe Node to your computer and configure a master role in selected network. 

    Cellframe Mastenode installation script will attempt to locate a .dwallet file in the same directory where it is located. 
    We recommend to use this option and copy the wallet file prior to launching the masternode configuration. 

    Alternatively, seed phrase from your wallet (24 words + password) can be used to restore the wallet that was created in Cellframe Dashboard.

    How to begin masternode configuration? 

    Run CMI.sh script with a desired network as a parameter. If network name is not provided, Backbone will be selected by default.

    Example:
        bash CMI.sh -n Backbone
        bash CMI.sh -n KelVPN

    Additionally, an option to provide a link to cellframe-node .deb file is available. 
    If not provided, latest available release will be used.

    Example:
        bash CMI.sh -n Backbone -l https://pub.cellframe.net/linux/cellframe-node/master/cellframe-node-5.3-342-rwd-amd64.deb

    In case any issues are encountered during the masternode configuration, contact the original author of the script or Cellframe Support team.

    Originally created by hyttmi  
    @CELLgainz in Telegram 

    Cellframe Support group in Telegram: https://t.me/cellframetechsupport
    Cellframe Support e-mail address: tech_support@demlabs.net

EOF

exit 
}


## parsing command-line options and arguments 

optstring=n:l:h

while getopts $optstring opt
do
  case $opt in
    n) NET_NAME=$OPTARG ;;
    l) NODE_DEB_LINK=$OPTARG ;;
    h) Help ;;
    *) exit 1 ;;
  esac
done


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
    echo "--- Cellframe-node is running..."
    printf "\n"
}

verify_exec_permissions ()
{

if [ -f $CELLFRAME_NODE_CLI_PATH ] && [ ! -x $CELLFRAME_NODE_CLI_PATH ]; then
    chmod +x $CELLFRAME_NODE_CLI_PATH #Make sure cli is executable
fi

if [ -f $CELLFRAME_NODE_CONFIG_PATH ] && [ ! -x $CELLFRAME_NODE_CONFIG_PATH ]; then
    chmod +x $CELLFRAME_NODE_CONFIG_PATH #Make sure config is executable
fi

if [ -f $CELLFRAME_NODE_TOOL_PATH ] && [ ! -x $CELLFRAME_NODE_TOOL_PATH ]; then
    chmod +x $CELLFRAME_NODE_TOOL_PATH #Make sure tool is executable
fi

}


run_cli() {
    /opt/cellframe-node/bin/cellframe-node-cli "$@"
}

restart_node ()
{
    systemctl restart cellframe-node.service
}

showinfo() {

    printf "%s Cellframe Mastenode installation script launched.\n" "---"

    read -p "--- Are you sure you want to continue? (Y/N) " confirm
    if [[ $confirm =~ ^[yY]$ ]]; then
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

check_deps() 
{
    echo "--- Checking necessary dependencies..."
    DEPS=( sed apt wget sha256sum wc pv irqbalance dig ) 
    for i in ${DEPS[@]}
    do
        if [[ $(command -v $i) ]]; then
            echo -e "\t==> $i found, continuing..."
        else
            echo -e "\t==> $i not found, installing..."
            apt-get update
            apt-get -y install wget pv psmisc irqbalance jq dnsutils
            break
        fi
    done
    check_if_link_provided
}

check_if_link_provided()
{
if [[ -z ${NODE_DEB_LINK} ]];
then 
    printf "Link to the cellframe-node package is not provided. Latest release from master branch will be used.\n"
    download_latest
elif [[ -n ${NODE_DEB_LINK} ]];
then
    printf "Link to the cellframe-node package is provided.\n"
    check_if_correct_link ${NODE_DEB_LINK}
fi 
}

check_if_correct_link()
{

if [[ $1 =~ https:\/\/pub\.cellframe\.net\/linux\/cellframe-node\/* ]]; 
then
  wget --spider -q $1
  if [ $? -eq 0 ]; 
  then
    printf "Correct link provided, file exists.\n"
    check_correct_arch_in_link
  else
    printf "Error! File doesn't exist! Latest release from master branch will be used.\n"
    download_latest
  fi
else 
    printf "Incorrect link provided. Latest release from master branch will be used.\n"
    download_latest
fi 
}

check_correct_arch_in_link()
{
_temp=${NODE_DEB_LINK##*-}
LINK_ARCH=${_temp%.*}

if [[ ${ARCH} == ${LINK_ARCH} ]];
then 
    printf "Link with compatible node architecture provided. Continuing...\n"
    download_from_link
else
    printf "Link with incompatible node architecture provided. Latest compatible release from master branch will be used.\n"
    download_latest
fi 
}


download_latest()
{
ARCH=$(dpkg --print-architecture)

NODE_VERSION=$(curl -v --silent https://pub.cellframe.net/linux/cellframe-node/master/ 2>&1 | grep -oP ">cellframe-node-\K5.3.[0-9]{3}" | sort | tail -n1)
printf "Latest available cellframe-node version on pub.cellframe.net: %s\n" "${NODE_VERSION}"

case "$ARCH" in 
  amd64) LATEST_FILE_NAME=$(wget -qO- https://pub.cellframe.net/linux/cellframe-node/master/ | grep -oP "\Kcellframe-node-5.3.[0-9]{3}-rwd-amd64.deb" | sort | tail -n1)
  ;;
  arm64) LATEST_FILE_NAME=$(wget -qO- https://pub.cellframe.net/linux/cellframe-node/master/ | grep -oP "\Kcellframe-node-5.3.[0-9]{3}-arm64.deb" | sort | tail -n1)
  ;;
  armhf) LATEST_FILE_NAME=$(wget -qO- https://pub.cellframe.net/linux/cellframe-node/master/ | grep -oP "\Kcellframe-node-5.3.[0-9]{3}-armhf.deb" | sort | tail -n1)
  ;;
  *) echo "Unsupported architecture, exiting..." && exit 1
  ;;
esac

echo "--- Downloading latest version of Cellframe node..."
wget -q https://pub.cellframe.net/linux/cellframe-node/master/${LATEST_FILE_NAME}

install_node
}

download_from_link()
{
printf "Downloading cellframe-node using provided link.\n"
wget -q ${NODE_DEB_LINK}

LATEST_FILE_NAME=$(echo ${NODE_DEB_LINK} | awk -F/ '{print $(NF)}')
install_node
}

install_node()
{
echo "--- Installing ${LATEST_FILE_NAME}..."
DEBIAN_FRONTEND=noninteractive dpkg -i ${LATEST_FILE_NAME}

verify_node_running
verify_exec_permissions
configure_networks
}


configure_networks()
{
NET_LIST=( Backbone KelVPN raiden riemann )

if echo ${NET_LIST[@]^^} | grep -qw ${NET_NAME^^};      # check for valid netname
then
    for i in "${NET_LIST[@]}"
    do 
        if [[ ${NET_NAME^^} == ${i^^} ]];
        then 
            NET_NAME=${i}       # overwrite NET_NAME in case input was not case-sensitive
        fi
    done  
else
    NET_NAME=Backbone
    printf "Provided unknown network name. Proceeding with masternode configuration for Backbone network.\n"
fi


if [[ -z ${NET_NAME} ]];    ## check if no netname input 
then 
    NET_NAME=Backbone
    printf "Network name is not provided. Proceeding with masternode configuration for Backbone network.\n"
fi 

printf "Configuring cellframe-node networks.\n" | tee -a $LOG
for _net in "${NET_LIST[@]}"
do 
    if [[ ${NET_NAME^^} == ${_net^^} ]];
    then 
        _state=on
    else 
        _state=off
    fi
    printf "Turning %s %s network.\n" "${_state}" "${_net}" | tee -a $LOG
    /opt/cellframe-node/bin/cellframe-node-config -e network ${_net} ensure ${_state}
    printf "\n"
done 

restart_node 
verify_node_running
create_cert
}

create_cert() {
    read -p "--- Input a desired name to your certificate (press ENTER for default name): " cert
    cert=${cert:-master}
        if [[ $cert =~ ^[a-zA-Z0-9]*$ ]]; then
            echo "--- Your certificate ${NET_NAME}.${cert} will be created..."
            /opt/cellframe-node/bin/cellframe-node-tool cert create ${NET_NAME}.${cert} sig_dil | tee -a $LOG 
            declare -x -g CERT="${NET_NAME}.${cert}"
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
                check_wallet_password
                declare -x -g WALLETADDRESS=$(run_cli wallet info -w $WALLETNAME -net ${NET_NAME} | grep -oP 'addr: \K.*$')
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
                check_wallet_password
                declare -x -g WALLETADDRESS=$(run_cli wallet info -w $WALLETNAME -net ${NET_NAME} | grep -oP 'addr: \K.*$')
                configure_node
            done
        fi
    else
        create_wallet
    fi
}

check_wallet_password()
{
if [[ $( run_cli wallet info -w ${WALLETNAME} -net ${NET_NAME} | grep error ) ]];
then 
    printf "%s Wallet is password protected.\n" "---"
    read -p "--- Enter wallet password to unlock it: " _password
    until [[ $( run_cli wallet activate -w ${WALLETNAME} -password ${_password} | grep activated ) ]];
    do 
        read -p "--- Incorrect wallet password. Try again: " _password
    done 
    printf "%s Wallet activated.\n" "---"
elif [[ $( run_cli wallet info -w ${WALLETNAME} -net ${NET_NAME} | grep addr ) ]];
then 
    printf "%s Wallet is not password protected.\n" "---"
fi 
}


create_wallet() {
    read -p "--- Input a desired name to your wallet: " walletname
        if [[ $walletname =~ ^[a-zA-Z0-9]*$ ]]; then
            echo "--- Your wallet $walletname will be created..." | tee -a $LOG
            declare -x -g WALLETNAME=$walletname
            get_seed
        else
            echo "--- Supported characters are a-z, A-Z, 0-9. No spaces."
            create_wallet
        fi
}

get_seed() 
{
    get_sign
    
    read -p "--- Is your wallet password protected? (Y/N) " _if_password

    if [[ ${_if_password} =~ ^[yY]$ ]]; 
    then
        _word_num=25
        _message="Input your 24 word seed phrase plus a password as 25th word!"
    else
        _word_num=24
        _message="Input your 24 word seed phrase."
    fi 

    printf "%s %s\n" "---" "${_message}"
    read -p "---> " words

    count=$(echo $words | wc -w)
    if [[ $count -eq ${_word_num} ]]; then
        SHA256=$(echo -n $words | tr -d [:blank:] | sha256sum | cut -d " " -f1)
        echo "--- Your SHA256SUM of seed phrase is: $SHA256"
        run_cli wallet new -w $WALLETNAME -sign ${_sign_type} -restore 0x$SHA256 -force | tee -a $LOG
        declare -x -g WALLETADDRESS=$(run_cli wallet info -w $WALLETNAME -net ${NET_NAME} | grep -oP 'addr: \K.*$')
        printf "%s Your address in %s: %s\n" "---" "${NET_NAME}" "${WALLETADDRESS}" | tee -a $LOG
        configure_node
    else
        echo "--- Not a ${_word_num} word seed phrase, your seed phrase had $count words!"
        get_seed
    fi
}

get_sign()
{
_signs_available=( sig_dil sig_falcon sig_sphincs )
_signs_number=${#_signs_available[@]}
_MAX_VALUE=$(($_signs_number - 1))

printf "%s Select the signature which was used when wallet was first created.\n" "---"
printf "%s Default signature in Cellframe Dashboard is CRYSTALS-Dilithium - sig_dil \n" "---"
printf "%s Available options: \n" "---"

for i in ${!_signs_available[@]}
do
    echo -e "\t==> [$i] -- ${_signs_available[$i]}"
done

read -p "---> Enter number: " number

if [[ $number =~ ^[0-9]$ && ! $number -gt $_MAX_VALUE ]]; 
then
    declare -x -g _sign_type=${_signs_available[${number}]}
    printf "%s %s signature selected.\n" "---" "${_sign_type}" | tee -a $LOG
else 
    printf "%s Not a valid number!\n\n" "---"
    get_sign 
fi 
}

configure_node() {
    NODE_CONFIG_FILE="/opt/cellframe-node/etc/cellframe-node.cfg"
    NET_CONFIG_FILE="/opt/cellframe-node/etc/network/${NET_NAME}.cfg"
    declare -x -g NODE_ADDR=$(run_cli net -net ${NET_NAME} get status | grep -oP '[0-9A-Z]{4}::[0-9A-Z]{4}::[0-9A-Z]{4}::[0-9A-Z]{4}')
    printf "Node address: %s \n" "${NODE_ADDR}" | tee -a $LOG  > /dev/null
    collectamount='10'
    NODE_ROLE=master

    echo "--- Modifying ${NET_NAME} configuration..."

    # deleting template lines 
    sed -i '/esbocs/d' ${NET_CONFIG_FILE}
    sed -i '/consensus_debug/d' ${NET_CONFIG_FILE}
    sed -i '/blocks-sign-cert/d' ${NET_CONFIG_FILE}
    sed -i '/collecting_level/d' ${NET_CONFIG_FILE}
    sed -i '/fee_addr/d' ${NET_CONFIG_FILE}
    
    # entering new configuration
    sed -i "s/^node-role=.*/node-role=${NODE_ROLE}/g" $NET_CONFIG_FILE
    echo "[esbocs]" >> $NET_CONFIG_FILE
    echo "blocks-sign-cert=$CERT" >> $NET_CONFIG_FILE
    echo "fee_addr=$WALLETADDRESS" >> $NET_CONFIG_FILE
    echo "collecting_level=$collectamount" >> $NET_CONFIG_FILE
    echo "consensus_debug=true" >> $NET_CONFIG_FILE

    echo "--- Modifying cellframe-node configuration..."

    sed -i "s/^debug_mode=.*/debug_mode=true/g" $NODE_CONFIG_FILE
    sed -i "0,/^enabled=.*/s/^enabled=.*/enabled=true/" $NODE_CONFIG_FILE
    sed -i "s/^auto_proc=.*/auto_proc=true/g" $NODE_CONFIG_FILE

    restart_node
    verify_node_running
    check_net_state
    sync_progress
}

check_net_state()
{
_not_ready=( NET_STATE_LINKS_PREPARE NET_STATE_LINKS_CONNECTING NET_STATE_LOADING NET_STATE_LINKS_ESTABLISHED )
_current_state=$( run_cli net -net ${NET_NAME} get status | grep -A1 states | grep current | cut -d: -f2 | tr -d ' ' ) 

while true;
do 
    if [[ ${_not_ready[@]} =~ ${_current_state} ]];
    then 
        printf "Cellframe Node is loading. Current network state: %s\n" "${_current_state}"
        sleep 10
        _current_state=$( run_cli net -net ${NET_NAME} get status | grep -A1 states | grep current | cut -d: -f2 | tr -d ' ' ) 
    else 
        break 
    fi
done 

printf "Cellframe Node loaded. Current network state: %s\n\n" "${_current_state}"
}


check_chain_sync()
{
_chain=$1
_sync_progress=$( run_cli net -net ${NET_NAME} get status | grep -A4 ${_chain} | grep percent | cut -d: -f2 | cut -d. -f1 )
}


sync_progress()
{

check_chain_sync zerochain

until [[ ${_sync_progress} -eq 100 ]]
do 
    printf "%s synchronization in progress.\n" "${_chain^}"
    printf "Progress: %s %s\n" "${_sync_progress}" "%"
    sleep 30
    check_chain_sync zerochain
done

printf "%s is fully synchronized at 100 %s\n\n" "${_chain^}" "%" | tee -a $LOG

sleep 5

check_chain_sync main 

until [[ ${_sync_progress} -eq 100 ]]
do 
    printf "%s synchronization in progress.\n" "${_chain^}"
    printf "Progress: %s %s\n" "${_sync_progress}" "%"
    sleep 10
    check_chain_sync main
done

printf "%s is fully synchronized at 100 %s\n\n" "${_chain^}" "%" | tee -a $LOG

publish_node
}


publish_node()
{
for _count in {1..10}
do 
    echo "--- Publishing node...."
    publish_result=$( run_cli node add -net ${NET_NAME} ) 
    sleep 5

    if [[ $( echo ${publish_result} | grep "error" ) ]]; 
    then
        publish_check=$( run_cli node list -net ${NET_NAME} ) 

        if [[ $( echo ${publish_check} | grep "${NODE_ADDR}" ) ]];
        then 
            printf "\tNode successfully added to %s node list.\n\n" "${NET_NAME}" | tee -a $LOG
            create_diag_data
        else
            echo "--- Attempt failed. Trying again in 10 seconds."
            sleep 10
        fi
        
    elif [[ $( echo ${publish_result}  | grep "Successfully" ) ]];
    then
        printf "\tNode successfully added to %s node list.\n\n" "${NET_NAME}" | tee -a $LOG
        create_diag_data
    else
        printf "Something went wrong while publishing node.\n"
        printf "Publish error:\n"
        printf "%s\n" "${publish_result}"
        printf "Exiting script...\n"
        exit 1
    fi
done 

printf "Not able to publish node. Are you behind a firewall/NAT? Check if port 8079 is open.\n" | tee -a $LOG
printf "Exiting script...\n" 
exit 1
}

create_diag_data()
{
echo "--- Adding diagnostics data file to /opt/cellframe-node/etc/diagdata.json..."
IP=$(dig @resolver1.opendns.com myip.opendns.com +short)
echo "{\"name\":\"${NODE_ADDR}\", \"category\":\"validator\", \"ip_addr\": \"${IP}\"}" > /opt/cellframe-node/etc/diagdata.json
printf "\n"

check_wallet_password
check_token_balance ${mtoken_array[${NET_NAME}]}
check_token_balance ${token_array[${NET_NAME}]}
lock_mtoken
}

check_token_balance() {

    token=$1

    if [[ ${token} = m* ]];
    then 
        _accept_value=$( run_cli srv_stake list keys -net ${NET_NAME} | grep -w key_delegating_min_value | cut -d: -f2 | cut -d. -f1 )
        _message="Minimum required amount to start masternode:"
    else 
        _accept_value='1'
        _message="Recommended amount for operations:"
    fi

    printf "%s Checking your %s balance...\n" "---" "${token}"
    BALANCE=$(run_cli wallet info -w ${WALLETNAME} -net ${NET_NAME} | grep -B3 -w ${token} | grep coins | cut -d: -f2 | cut -d. -f1)
    if [[ ${BALANCE} -lt ${_accept_value} ]]; 
    then
        printf "%s Looks like you don't have enough %s on your wallet.\n" "---" "${token}" | tee -a $LOG
        printf "%s Your balance: %s %s\n" "---" "${BALANCE:-0}" "${token}"
        printf "%s %s %s %s\n\n" "---" "${_message}" "${_accept_value}" "${token}"
        printf "Exiting script...\n"
        exit 1
    else
        printf "%s Enough %s found on wallet.\n" "---" "${token}" | tee -a $LOG
        printf "%s Your balance: %s %s\n\n" "---" "${BALANCE}" "${token}"
    fi
}


lock_mtoken() {
    token=${mtoken_array[${NET_NAME}]}
    BALANCE=$(run_cli wallet info -w ${WALLETNAME} -net ${NET_NAME} | grep -B3 -w ${token} | grep coins | cut -d: -f2 | cut -d. -f1)
    printf "%s Your current wallet balance is %s %s \n" "---" ${BALANCE} ${mtoken_array[${NET_NAME}]}
    read -p "Enter the amount which you want to lock for your mastenode (no decimals): " mtoken_amount
    if [[ ! ${mtoken_amount} =~ ^[0-9]*$ ]]; 
    then
        echo "--- Invalid amount of tokens! Please try again..."
        lock_mtoken
    elif [[ ${mtoken_amount} -gt ${BALANCE} ]];
    then 
        printf "%s Entered amount is greater than available %s on wallet! Please try again...\n" "---" "${token}"
        lock_mtoken
    else
        echo "--- Delegating stake..."
        delegate_result=$( run_cli srv_stake delegate -cert $CERT -net ${NET_NAME} -w ${WALLETNAME} -value ${mtoken_amount}.0e+18 -fee 0.05e+18 )

        if [[ $( echo ${delegate_result} | grep "success" ) ]];
        then 
            delegate_hash=$( printf "${delegate_result}\n" | grep tx_hash | cut -d: -f2 )
            printf "Transaction created successfully. Tx hash: %s\n" "${delegate_hash}" | tee -a $LOG
            msg_ready
        elif [[ $( echo ${delegate_result} | grep "error" ) ]];
        then 
            printf "Something went wrong. Transaction was not created.\n" | tee -a $LOG
            printf "${delegate_result}\n" | tee -a $LOG
            exit 1
        fi 
    fi
}

msg_ready()
{
printf "\nCongratulations, masternode in %s network is successfully configured!\n" "${NET_NAME}"
printf "Please contact Cellframe Support team and send your transaction hash for masternode approval.\n"
printf "Hash of transaction that locked %s %s: %s\n" "${mtoken_amount}" "${mtoken_array[${NET_NAME}]}" "${delegate_hash}"
printf "Cellframe Support group in Telegram: %s\n" "https://t.me/cellframetechsupport" 
printf "Cellframe Support e-mail address: %s\n" "tech_support@demlabs.net"

printf "\nAfter receiving approval from Cellframe Support team, two more things need to be done for the proper masternode functioning.\n"
printf "We recommend to save the following information for quick and easy completion of the setup.\n"
printf "%s A validator fee order needs to be created. Cellframe-node-cli command:\n" "---> 1."
printf "/opt/cellframe-node/bin/cellframe-node-cli srv_stake order create -net %s -value %se+18 -cert %s\n\n" "${NET_NAME}" "${fee_order_array[${NET_NAME}]}" "${CERT}"
printf "%s Cellframe-node needs to be restarted. Command:\n" "---> 2."
printf "systemctl restart cellframe-node.service\n\n"

printf "Cellframe Masternode Installer log file is available at %s\n" "${LOG}"
read -p "Do you want to view it? (Y/N) " confirm
if [[ $confirm =~ ^[yY]$ ]]; then
    cat $LOG
else
    exit
fi

exit 
}


check_root
