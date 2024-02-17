import utils
import re
import os

def generateHtml():
  script_dir = os.path.dirname(os.path.realpath(__file__))
  template = f"{script_dir}/template.html"
  hostname = utils.getHostname()
  sysuptime = utils.getSystemUptime()
  nodeuptime = utils.getNodeUptime()
  currentnodeversion = utils.getCurrentNodeVersion()
  latestnodeversion = utils.getLatestNodeVersion()
  cpustats = utils.getCPUStats()
  memstats = utils.getMemoryStats()
  networkinfo = utils.generateNetworkHTML()
  with open(template, "r") as file:
    html_template = file.read()


  html = html_template.format(
    HOSTNAME=hostname,
    UPTIME=sysuptime,
    ACTIVETIME=nodeuptime,
    CURRENT_VERSION=currentnodeversion,
    LATEST_VERSION=latestnodeversion,
    CPU_UTILIZATION=cpustats,
    MEMORY_UTILIZATION=memstats,
    NETWORKINFO=networkinfo
  )
  return html