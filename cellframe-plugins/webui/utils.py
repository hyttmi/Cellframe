import DAP
from pycfhelpers.node.logging import CFLog
from pycfhelpers.node.net import CFNet
import subprocess, socket, urllib.request, re, time

def getConfigValue(section, key, default=None, cast=None):
    try:
        value = DAP.configGetItem(section, key)
        if cast is not None:
            value = cast(value)
        return value
    except ValueError:
        return default

PLUGIN_NAME = "[Cellframe system & node info by Mika H (@CELLgainz)]"
PLUGIN_URI = getConfigValue("webui", "uri", default="webui")

log = CFLog()

def log_notice(msg):
    log.notice(f"{PLUGIN_NAME} {msg}")
    
def log_error(msg):
    log.error(f"{PLUGIN_NAME} {msg}")

def CLICommand(command):
    full_command = ["/opt/cellframe-node/bin/cellframe-node-cli"] + command.strip().split()
    log_notice(f"Running command: {' '.join(full_command)}")

    try:
        process = subprocess.Popen(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout_lines = []
        for line in process.stdout:
            stdout_lines.append(line.strip())
        
        stderr = process.stderr.read().strip()
        
        process.wait(timeout=10)
        
        if process.returncode == 0:
            return "\n".join(stdout_lines)
        else:
            log_error(f"Command '{' '.join(full_command)}' failed with error: {stderr}")
            return f"Command '{' '.join(full_command)}' failed with error: {stderr}"
    
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        log_error(f"Command {' '.join(full_command)} timed out!")
        return f"Command {' '.join(full_command)} timed out!"
    except Exception as e:
        log_error(f"An error occurred: {e}")
        return f"An error occurred: {e}"


def shellCommand(command):
    command = f"{command.strip()}"
    log_notice(f"Running command: {command}")

    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(timeout=10)
        
        if process.returncode == 0:
            return stdout.strip()
        else:
            log_error(f"Command '{command}' failed with error: {stderr.strip()}")
            return f"Command '{command}' failed with error: {stderr.strip()}"
    
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        log_error(f"Command {command} timed out!")
        return f"Command {command} timed out!"
    except Exception as e:
        log_error(f"An error occurred: {e}")
        return f"An error occurred: {e}"

def getPID():
    return shellCommand("pgrep -x cellframe-node")

def getHostname():
    return socket.gethostname()

def getExtIP():
    try:
        with urllib.request.urlopen('https://ifconfig.me/ip') as response:
            ip_address = response.read().decode('utf-8').strip()
            return ip_address
    except Exception as e:
        log_error(f"Error: {e}")
        return f"Error: {e}"

def getSystemUptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])

        uptime_struct = time.gmtime(uptime_seconds)
        days = uptime_struct.tm_yday - 1
        hours = uptime_struct.tm_hour
        minutes = uptime_struct.tm_min
        seconds = uptime_struct.tm_sec
        uptime_str = f"{days}-{hours:02}:{minutes:02}:{seconds:02}" if days > 0 else f"{hours:02}:{minutes:02}:{seconds:02}"

        return uptime_str
    except Exception as e:
        log_error(f"Error {e}")
        return f"Error {e}"

def getNodeUptime():
    PID = getPID()
    return shellCommand(f"ps -p {PID} -o etime= | sed 's/^[[:space:]]*//'")

def getCurrentNodeVersion():
    version = CLICommand("version").replace("-",".")
    return version.split()[2]

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
    return shellCommand(f"ps -p {PID} -o %cpu= | tr -d '[:blank:]'")

def getMemoryStats():
    PID = getPID()
    rss_kb = shellCommand(f"ps -p {PID} -o rss= | tr -d '[:blank:]'")
    rss_mb = round(int(rss_kb) / 1024, 2)
    return rss_mb

def getListNetworks():
    return CFNet.active_nets() or None

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

def getAllBlocks(network):
    all_blocks_cmd = CLICommand(f"block count -net {network}")
    pattern_all_blocks = r":\s+(\d+)"
    all_blocks_match = re.search(pattern_all_blocks, all_blocks_cmd)
    if all_blocks_match:
        return all_blocks_match.group(1)
    else:
        return None

def getFirstSignedBlocks(network):
    net_config = readNetworkConfig(network)
    if net_config is not None:
        cmd_get_first_signed_blocks = CLICommand(f"block list -net {network} chain -main first_signed -cert {net_config[0]} -limit 1")
        pattern = r"have blocks: (\d+)"
        blocks_match = re.search(pattern, cmd_get_first_signed_blocks)
        if blocks_match:
            result = blocks_match.group(1)
            return result
    else:
        return None

def getAllSignedBlocks(network):
    net_config = readNetworkConfig(network)
    if net_config is not None:
        cmd_get_all_signed_blocks = CLICommand(f"block list -net {network} chain -main signed -cert {net_config[0]} -limit 1")
        pattern = r"have blocks: (\d+)"
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
            balance_pattern = r"coins:\s+([\d.]+)[\s\S]+?ticker:\s+(\w+)"
            tokens = re.findall(balance_pattern, cmd_get_wallet_info)
            return tokens
    else:
        return None
    
def getRewards(network):
    net_config = readNetworkConfig(network)
    if net_config is not None:
        cmd_get_autocollect_rewards = CLICommand(f"block -net {network} autocollect status")
        if cmd_get_autocollect_rewards:
            amount_pattern = r"profit is (\d+.\d+)"
            amounts = re.findall(amount_pattern, cmd_get_autocollect_rewards)
            total_amount = sum(float(amount) for amount in amounts)
            return total_amount
    else:
        return None

    
def generateNetworkData():
    networks = getListNetworks()
    if networks is not None:
        network_data = []
        for network in networks:
            net_status = CLICommand(f"net -net {network} get status")
            addr_pattern = r"([A-Z0-9]*::[A-Z0-9]*::[A-Z0-9]*::[A-Z0-9]*)"
            state_pattern = r"states:\s+current: (\w+)"
            target_state_pattern = r"target: (\w+)"
            addr_match = re.search(addr_pattern, net_status)
            state_match = re.search(state_pattern, net_status)
            target_state_match = re.search(target_state_pattern, net_status)
            tokens = getFeeWalletTokens(network)
            
            if state_match and target_state_match:
                network_info = {
                    'name': network,
                    'state': state_match.group(1),
                    'target_state': target_state_match.group(1),
                    'address': addr_match.group(1),
                    'first_signed_blocks': getFirstSignedBlocks(network),
                    'all_signed_blocks': getAllSignedBlocks(network),
                    'all_blocks': getAllBlocks(network),
                    'autocollect_status': getAutocollectStatus(network),
                    'rewards': getRewards(network),
                    'fee_wallet_tokens': [{'token': token[1], 'balance': token[0]} for token in tokens] if tokens else None
                }
                network_data.append(network_info)
            else:
                return None
    
        return network_data
    else:
        return None
