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
    cpu_stats = shellCommand(f"ps -p {PID} -o %cpu= | sed 's/^[[:space:]]*//'")
    return cpu_stats

def getMemoryStats():
    PID = getPID()
    mem_stats = shellCommand(f"ps -p {PID} -o %mem= | sed 's/^[[:space:]]*//'")
    return mem_stats

def getListNetworks():
    networks = CLICommand("net list")
    networks = networks.split()
    networks = networks[1:]
    return networks

def getAutocollectStatus(network):
    autocollect_cmd = CLICommand(f"block autocollect status -net {network} -chain main")
    if not "is active" in autocollect_cmd:
        return "Autocollect status is inactive"
    else:
        return "Autocollect status is active"
    
def readNetworkConfig(network):
    net_config = []
    config_file = f"/opt/cellframe-node/etc/network/{network}.cfg"
    with open(config_file, "r") as file:
        text = file.read()
    pattern_cert = r"^blocks-sign-cert=(.+)$"
    pattern_wallet = r"^fee_addr=(.+)$"
    cert_match = re.search(pattern_cert, text)
    wallet_match = re.search(pattern_wallet, text)
    if cert_match and wallet_match:
        net_config.append(cert_match.group(1))
        net_config.append(wallet_match.group(1))
        return net_config
    else:
        return None
    
def getFirstSignedBlocks(network):
    net_config = readNetworkConfig(network)
    cmd_get_first_signed_blocks = CLICommand("cellframe-node-cli block -net {network} -chain main list signed -cert {net_config[0]}")
    pattern = r"Have (\d+) blocks"
    blocks_match = re.search(pattern, cmd_get_first_signed_blocks)
    if blocks_match:
        return blocks_match.group(1)
    else:
        return None

def generateNetworkHTML():
  networks = getListNetworks()
  html = ""
  for network in networks:
    net_status = CLICommand(f"net -net {network} get status")
    status_pattern = r"has state (\w+) \(target state (\w+)\).*address ([A-Z0-9]*::[A-Z0-9]*::[A-Z0-9]*::[A-Z0-9]*)"
    match = re.search(status_pattern, net_status)
    autocollect_status = getAutocollectStatus(network)
    network_config = readNetworkConfig(network)
    
    if match:
      state = match.group(1)
      target_state = match.group(2)
      address = match.group(3)

      html += f'''
      <div class="row">
      <button data-bs-toggle="collapse" data-bs-target=".{network}" aria-expanded="false" class="mx-auto btn btn-custom">{network}</button>
      </div>
      <div class="{network} row collapse">
      <pre class="stats mx-auto">
      <table border="0" class="mx-auto">
        <tr>
          <td>Network state:</td>
          <td>{state}</td>
        </tr>
        <tr>
          <td>Target state:</td>
          <td>{target_state}</td>
        </tr>
        <tr>
          <td>Node address:</td>
          <td>{address}</td>
        </tr>
      </table>
      </pre>
      </div>
      <div class="{network} row collapse">
      <pre class="stats mx-auto">
      {autocollect_status}
      </pre>
      </div>
      '''
    else:
      html += f'''
      <div class="{network} row collapse">
        <pre class="stats mx-auto">No data available for {network}</pre>
      </div>
      '''

  return html


