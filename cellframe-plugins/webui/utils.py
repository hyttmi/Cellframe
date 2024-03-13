import DAP
from DAP.Core import logIt
from CellFrame.Network import Net
import subprocess, socket, urllib.request, re, os, time

def get_config_value(section, key, default=None, cast=None):
    try:
        value = DAP.configGetItem(section, key)
        if cast is not None:
            value = cast(value)
        return value
    except ValueError:
        return default

def debug(fn):
    def wrapper(*args, **kwargs):
        dbg_enabled = get_config_value("webui", "debug")
        if dbg_enabled:
            logIt.notice(f"[DBG] (Cellframe Masternode WebUI) Invoking {fn.__name__}")
            logIt.notice(f"[DBG] (Cellframe Masternode WebUI) args: {args}")
            logIt.notice(f"[DBG] (Cellframe Masternode WebUI) kwargs: {kwargs}")
            result = fn(*args, **kwargs)
            logIt.notice(f"[DBG] (Cellframe Masternode WebUI) returned {result}")
            return result
        else:
            return fn(*args, **kwargs)
    return wrapper

@debug
def CLICommand(command):
    full_command = f"/opt/cellframe-node/bin/cellframe-node-cli {command}"
    try:
        result = subprocess.check_output(full_command, shell=True, text=True).strip()
        return result
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

@debug
def shellCommand(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True).strip()
        return result
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

@debug
def getPID():
    return os.getpid()

@debug
def getHostname():
    return socket.gethostname()

@debug
def getExtIP():
    try:
        with urllib.request.urlopen('https://ifconfig.me/ip') as response:
            ip_address = response.read().decode('utf-8').strip()
            return ip_address
    except Exception as e:
        return f"An error occurred: {e}"

@debug
def getSystemUptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])

    uptime_struct = time.gmtime(uptime_seconds)
    days = uptime_struct.tm_yday - 1
    hours = uptime_struct.tm_hour
    minutes = uptime_struct.tm_min
    seconds = uptime_struct.tm_sec
    uptime_str = f"{days}-{hours:02}:{minutes:02}:{seconds:02}" if days > 0 else f"{hours:02}:{minutes:02}:{seconds:02}"

    return uptime_str

@debug
def getNodeUptime():
    PID = getPID()
    return shellCommand(f"ps -p {PID} -o etime= | sed 's/^[[:space:]]*//'")

@debug
def getCurrentNodeVersion():
    version = CLICommand("version").replace("-",".")
    return version.split()[2]

@debug
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

@debug
def getCPUStats():
    PID = getPID()
    return shellCommand(f"ps -p {PID} -o %cpu= | tr -d '[:blank:]'")

@debug
def getMemoryStats():
    PID = getPID()
    return shellCommand(f"ps -p {PID} -o %mem= | tr -d '[:blank:]'")

@debug
def getListNetworks():
    networks = CLICommand("net list").replace(",","")
    return networks.split()[1:]

@debug
def getAutocollectStatus(network):
    autocollect_cmd = CLICommand(f"block autocollect status -net {network} -chain main")
    if not "is active" in autocollect_cmd:
        return "Inactive"
    else:
        return "Active"

@debug
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

@debug
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

@debug
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

@debug
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
    
@debug
def generateNetworkData():
    networks = getListNetworks()
    network_data = []
    for network in networks:
        net_status = CLICommand(f"net -net {network} get status")
        addr_pattern = r"([A-Z0-9]*::[A-Z0-9]*::[A-Z0-9]*::[A-Z0-9]*)"
        state_pattern = r"current: (\w+)"
        target_state_pattern = r"target: (\w+)"
        addr_match = re.search(addr_pattern, net_status)
        state_match = re.search(state_pattern, net_status)
        target_state_match = re.search(target_state_pattern, net_status)
        tokens = getFeeWalletTokens(network)
        
        if addr_match and state_match and target_state_match:
            network_info = {
                'name': network,
                'state': state_match.group(1),
                'target_state': target_state_match.group(1),
                'address': addr_match.group(1),
                'first_signed_blocks': getFirstSignedBlocks(network),
                'all_signed_blocks': getAllSignedBlocks(network),
                'autocollect_status': getAutocollectStatus(network),
                'fee_wallet_tokens': [{'token': token[2], 'balance': token[0]} for token in tokens] if tokens else None
            }

            network_data.append(network_info)
        else:
            return None

    return network_data
