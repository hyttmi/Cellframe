import subprocess
import socket
import urllib.request
import re
import os

def CLICommand(command):
    full_command = f"/opt/cellframe-node/bin/cellframe-node-cli {command}"
    try:
        result = subprocess.check_output(full_command, shell=True, text=True).strip()
        return result
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def shellCommand(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True).strip()
        return result
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def getPID():
    node_pid = os.getpid()
    return node_pid

def getCurrentVersion():
    currentversion = CLICommand("version")
    return currentversion

def getHostname():
    hostname = socket.gethostname()
    return hostname

def getSystemUptime():
    uptime = shellCommand("uptime -p")
    return uptime

def getNodeUptime():
    PID = getPID()
    uptime = shellCommand(f"ps -p {PID} -o etime= | sed 's/^[[:space:]]*//'")
    return uptime

def getCurrentNodeVersion():
    version = CLICommand("version")
    version = version.split()
    return version[2]

def getLatestNodeVersion():
    badge_url = "https://pub.cellframe.net/linux/cellframe-node/master/node-version-badge.svg"
    response = urllib.request.urlopen(badge_url)
    svg_content = response.read().decode('utf-8')
    version_pattern = r'>(\d.\d.\d+)'
    match = re.search(version_pattern, svg_content)
    if match:
        latest_version = match.group(1)
        return latest_version
    else:
        return "N/A"

def getCPUStats():
    PID = getPID()
    cpu_stats = shellCommand(f"ps -p {PID} -o %cpu= | tr -d '[:blank:]'")
    return cpu_stats

def getMemoryStats():
    PID = getPID()
    mem_stats = shellCommand(f"ps -p {PID} -o %mem= | tr -d '[:blank:]'")
    return mem_stats

def getListNetworks():
    networks = CLICommand("net list")
    networks = networks.split()
    networks = networks[1:]
    return networks

def getAutocollectStatus(network):
    autocollect_cmd = CLICommand(f"block autocollect status -net {network} -chain main")
    if not "is active" in autocollect_cmd:
        return "Inactive"
    else:
        return "Active"
    
def readNetworkConfig(network):
    net_config = []
    config_file = f"/opt/cellframe-node/etc/network/{network}.cfg"
    with open(config_file, "r") as file:
        text = file.read()
    pattern_cert = r"^blocks-sign-cert=(.+)"
    pattern_wallet = r"^fee_addr=(.+)"
    cert_match = re.search(pattern_cert, text, re.MULTILINE)
    wallet_match = re.search(pattern_wallet, text, re.MULTILINE)
    if cert_match and wallet_match:
        net_config.append(cert_match.group(1))
        net_config.append(wallet_match.group(1))
        return net_config
    else:
        return None
    
def getFirstSignedBlocks(network):
    net_config = readNetworkConfig(network)
    if net_config is not None:
        cmd_get_first_signed_blocks = CLICommand(f"block -net {network} -chain main list first_signed -cert {net_config[0]}")
        pattern = r"Have (\d+) blocks"
        blocks_match = re.search(pattern, cmd_get_first_signed_blocks)
        if blocks_match:
            result = blocks_match.group(1)
            return result
    else:
        return None

def getAllSignedBlocks(network):
    net_config = readNetworkConfig(network)
    if net_config is not None:
        cmd_get_all_signed_blocks = CLICommand(f"block -net {network} -chain main list signed -cert {net_config[0]}")
        pattern = r"Have (\d+) blocks"
        blocks_match = re.search(pattern, cmd_get_all_signed_blocks)
        if blocks_match:
            result = blocks_match.group(1)
            return result
    else:
        return None

def getFeeWalletTokens(network):
    net_config = readNetworkConfig(network)
    if net_config is not None:
        cmd_get_wallet_info = CLICommand(f"wallet info -addr {net_config[1]}")
        if cmd_get_wallet_info:
            balance_pattern = r"(\d+\.\d+)\s+\((\d+)\)\s*(\S+)"
            tokens = re.findall(balance_pattern, cmd_get_wallet_info)
            return tokens
    else:
        return None

def generateNetworkData():
    networks = getListNetworks()
    network_data = []

    for network in networks:
        net_status = CLICommand(f"net -net {network} get status")
        status_pattern = r"has state (\w+) \(target state (\w+)\).*address ([A-Z0-9]*::[A-Z0-9]*::[A-Z0-9]*::[A-Z0-9]*)"
        match = re.search(status_pattern, net_status)
        autocollect_status = getAutocollectStatus(network)
        get_first_signed_blocks = getFirstSignedBlocks(network)
        get_all_signed_blocks = getAllSignedBlocks(network)
        tokens = getFeeWalletTokens(network)
        
        if match:
            state = match.group(1)
            target_state = match.group(2)
            address = match.group(3)

            network_info = {
                'name': network,
                'state': state,
                'target_state': target_state,
                'address': address,
                'first_signed_blocks': get_first_signed_blocks,
                'all_signed_blocks': get_all_signed_blocks,
                'autocollect_status': autocollect_status,
                'fee_wallet_tokens': [{'token': token[2], 'balance': token[0]} for token in tokens]
            }

            network_data.append(network_info)
        else:
            network_data.append({
                'name': network,
                'error': f'No data available for {network}'
            })

    return network_data