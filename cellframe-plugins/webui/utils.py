from pycfhelpers.node.logging import CFLog
from pycfhelpers.node.net import CFNet
from command_runner import command_runner
import DAP
import socket, urllib.request, re, time, psutil
from datetime import datetime

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
    
def CLICommand(command, timeout=5):
    try:
        log_notice(f"Running command: {command}")
        exit_code, output = command_runner(f"/opt/cellframe-node/bin/cellframe-node-cli {command}", timeout=timeout)
        if exit_code == 0:
            return output.strip()
        else:
            log_error(f"Command failed with error: {output.strip()}")
            return f"Command failed with error: {output.strip()}"
    except Exception as e:
        log_error(f"Error: {e}")
        return f"Error: {e}"

def getPID():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == "cellframe-node":
            return proc.info['pid']
    return None

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

def format_uptime(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

def getSysStats():
    try:
        PID = getPID()
        process = psutil.Process(PID)

        sys_stats = {}

        cpu_usage = process.cpu_percent(interval=1)
        sys_stats['node_cpu_usage'] = cpu_usage if cpu_usage is not None else "N/A"

        memory_info = process.memory_info()
        memory_usage_mb = memory_info.rss / 1024 / 1024
        sys_stats['node_memory_usage_mb'] = round(memory_usage_mb, 2) if memory_usage_mb is not None else "N/A"
        
        create_time = process.create_time()
        uptime_seconds = time.time() - create_time
        sys_stats['node_uptime'] = format_uptime(uptime_seconds) if uptime_seconds is not None else "N/A"

        boot_time = psutil.boot_time()
        system_uptime_seconds = time.time() - boot_time
        sys_stats['system_uptime'] = format_uptime(system_uptime_seconds) if system_uptime_seconds is not None else "N/A"

        return sys_stats
    except Exception as e:
        log_error(f"Error: {e}")
        return f"Error {e}"


def getCurrentNodeVersion():
    version = CLICommand("version", 2).replace("-",".")
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

def getListNetworks():
    return CFNet.active_nets() or None

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

def getAutocollectStatus(network):
    autocollect_cmd = CLICommand(f"block autocollect status -net {network} -chain main")
    if not "is active" in autocollect_cmd:
        return "Inactive"
    else:
        return "Active"

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

def getSignedBlocksToday(network):
    net_config = readNetworkConfig(network)
    if net_config is not None:
        cmd_output = CLICommand(f"block list -net {network} signed -cert {net_config[0]}")
        today_str = datetime.now().strftime("%a, %d %b %Y")
        blocks_signed_today = 0

        lines = cmd_output.splitlines()
        for line in lines:
            if line.startswith("ts_create:") and today_str in line:
                log_notice(today_str)
                log_notice(line)
                blocks_signed_today += 1
        log_notice(f"Blocks signed today: {blocks_signed_today}")
        return blocks_signed_today

def getRewardWalletTokens(network):
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
            getSignedBlocksToday(network)
            net_status = CLICommand(f"net -net {network} get status")
            addr_pattern = r"([A-Z0-9]*::[A-Z0-9]*::[A-Z0-9]*::[A-Z0-9]*)"
            state_pattern = r"states:\s+current: (\w+)"
            target_state_pattern = r"target: (\w+)"
            addr_match = re.search(addr_pattern, net_status)
            state_match = re.search(state_pattern, net_status)
            target_state_match = re.search(target_state_pattern, net_status)
            tokens = getRewardWalletTokens(network)
            
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
