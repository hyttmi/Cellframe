import utils
import re
import os

def generateNetworkInfo():
  networks = utils.getListNetworks()
  html = ""
  for network in networks:
    net_status = utils.CLICommand(f"net -net {network} get status")
    status_pattern = r"has state (\w+) \(target state (\w+)\).*address ([A-Z0-9]*::[A-Z0-9]*::[A-Z0-9]*::[A-Z0-9]*)"
    match = re.search(status_pattern, net_status)
    autocollect_cmd = utils.CLICommand(f"block autocollect status -net {network} -chain main")
    if not "is active" in autocollect_cmd:
      autocollect_cmd = "Autocollect status is inactive"
    
    if match:
      state = match.group(1)
      target_state = match.group(2)
      address = match.group(3)

      html += f'''
      <button data-target="{network}" class="toggleButton btn btn-custom">{network}</button>
      <div class="row">
      <pre id="{network}" class="stats mx-auto">
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
          <td>Address:</td>
          <td>{address}</td>
        </tr>
      </table>
      {autocollect_cmd}
      </pre>
      </div>
      '''
    else:
      html += f'''
      <pre class="stats mx-auto">No data available for {network}</pre>
      '''

  return html

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
  networkinfo = generateNetworkInfo()
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