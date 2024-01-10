#!/bin/bash

# Check the number of command-line arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <token_from> <token_to>"
    exit 1
fi

# Function to check if the Cellframe node is running
is_node_running() {
    /opt/cellframe-node/bin/cellframe-node-cli net status >/dev/null 2>&1
}

# Function to list all networks
list_networks() {
    /opt/cellframe-node/bin/cellframe-node-cli net list | grep -oP '(?<=^\t)[^ ]+'
}

# Function to get open orders for a specific token pair on a network
get_open_orders() {
    local network=$1
    local token_from=$2
    local token_to=$3
    /opt/cellframe-node/bin/cellframe-node-cli srv_xchange orders -net "$network" -status opened -token_from "$token_from" -token_to "$token_to"
}

# Check if the Cellframe node is running
if ! is_node_running; then
    echo "Node is not running. Exiting."
    exit 1
fi

# Get a list of all networks
networks=$(list_networks)

# Array to store order information
declare -a order_info_array
declare -a seller_info_array
declare -a buyer_info_array

while read -r network; do
    token_to=$1
    token_from=$2

    # Get open orders for token_from to token_to
    orders=$(get_open_orders "$network" "$token_from" "$token_to")

    # Process each order and store information in the array
    while IFS= read -r line; do
        # Skip empty lines
        if [ -z "$line" ]; then
            continue
        fi

        # Extract order details
        if [[ $line =~ orderHash ]]; then
            order_hash=$(echo "$line" | grep -oP 'orderHash: \K[^ ]+')
        elif [[ $line =~ ts_created ]]; then
            ts_created=$(echo "$line" | grep -oP 'ts_created: \K(.*)' | cut -d'(' -f2 | cut -d')' -f1)
        elif [[ $line =~ Status ]]; then
            status=$(echo "$line" | grep -oP 'Status: \K[^,]+')
            amount=$(echo "$line" | grep -oP 'amount: \K[^ ]+')
            filled_ratio=$(echo "$line" | grep -oP 'filled: \K[^%]+')
            rate=$(echo "$line" | grep -oP 'rate \([^)]+\): \K[^,]+')
            rateval=$(echo "$rate" | bc)

            # Store all information in the array
            order_info_array+=("$order_hash,$amount,$token_from,$rateval,$token_to,$network")
        fi
    done <<< "$orders"

    # Repeat the process for orders from token_to to token_from
    orders=$(get_open_orders "$network" "$token_to" "$token_from")

    while IFS= read -r line; do
        # Skip empty lines
        if [ -z "$line" ]; then
            continue
        fi

        # Extract order details
        if [[ $line =~ orderHash ]]; then
            order_hash=$(echo "$line" | grep -oP 'orderHash: \K[^ ]+')
        elif [[ $line =~ ts_created ]]; then
            ts_created=$(echo "$line" | grep -oP 'ts_created: \K(.*)' | cut -d'(' -f2 | cut -d')' -f1)
        elif [[ $line =~ Status ]]; then
            status=$(echo "$line" | grep -oP 'Status: \K[^,]+')
            amount=$(echo "$line" | grep -oP 'amount: \K[^ ]+')
            filled_ratio=$(echo "$line" | grep -oP 'filled: \K[^%]+')
            rate=$(echo "$line" | grep -oP 'rate \([^)]+\): \K[^,]+')
            rateval=$(echo "$rate" | bc)

            # Store all information in the array
            order_info_array+=("$order_hash,$amount,$token_to,$rateval,$token_from,$network")
        fi
    done <<< "$orders"
done <<< "$networks"

# Sort the array based on the rate in ascending order for sellers
IFS=$'\n' seller_info_array=($(sort -t',' -k4n <<<"${seller_info_array[*]}"))

# Sort the array based on the rate in descending order for buyers
IFS=$'\n' buyer_info_array=($(sort -t',' -k6nr <<<"${buyer_info_array[*]}"))

# Display seller order details
echo "Seller Orderbook:"
for seller_info in "${seller_info_array[@]}"; do
    IFS=',' read -r order_hash amount token_from rate token_to network <<< "$seller_info"
    product=$(echo "scale=12; $rate * $amount" | bc)
    ppa=$(echo "scale=8;  ( $product / $amount )" | bc)
    echo "$order_hash, Selling $amount $token_from for $product $token_to ppa $ppa"
done

# Display buyer order details
echo "Buyer Orderbook:"
for buyer_info in "${buyer_info_array[@]}"; do
    IFS=',' read -r order_hash amount token_from rate token_to network <<< "$buyer_info"
    product=$(echo "scale=12; $rate * $amount" | bc)
    ppa=$(echo "scale=8; ( $amount /  $product  )" | bc)
    echo "$order_hash, Buying $product $token_to for $amount $token_from ppa $ppa"
done
