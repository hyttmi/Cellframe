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