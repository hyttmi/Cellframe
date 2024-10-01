from utils import *
import handlers

def generateHTML():
    sys_stats = getSysStats()
    is_update_available, curr_version, latest_version = checkForUpdate()

    info = {
        'update_available': is_update_available,
        'current_version': curr_version,
        'latest_version': latest_version,
        "title": PLUGIN_NAME,
        "hostname": getHostname(),
        "external_ip": getExtIP(),
        "system_uptime": sys_stats["system_uptime"],
        "node_uptime": sys_stats["node_uptime"],
        "node_version": getCurrentNodeVersion(),
        "latest_node_version": getLatestNodeVersion(),
        "networks": getListNetworks(),
        "cpu_utilization": sys_stats["node_cpu_usage"],
        "memory_utilization": sys_stats["node_memory_usage_mb"],
        "header_text": getConfigValue("webui", "header_text", default=False),
        "net_info": generateNetworkData()
    }

    template_setting = getConfigValue("webui", "template", default="cards")
    template_path = f"{template_setting}/template.html"
    try:
        logNotice(f"Generating HTML page...")
        template = handlers.env.get_template(template_path)
        output = template.render(info)
    except Exception as e:
        logError(f"Error in generating HTML: {e}")
        output = f"<h1>Got an error: {e}</h1>"
    return output

def generateEmail():
    sys_stats = getSysStats()

    info = {
        "title": PLUGIN_NAME,
        "system_uptime": sys_stats["system_uptime"],
        "node_uptime": sys_stats["node_uptime"],
        "node_version": getCurrentNodeVersion(),
        "latest_node_version": getLatestNodeVersion(),
        "cpu_utilization": sys_stats["node_cpu_usage"],
        "memory_utilization": sys_stats["node_memory_usage_mb"],
        "net_info": generateNetworkData()
    }

    template_setting = getConfigValue("webui", "template", default="cards")
    template_path = f"{template_setting}/mail.html"
    try:
        logNotice(f"Generating email...")
        template = handlers.env.get_template(template_path)
        output = template.render(info)
    except Exception as e:
        logError(f"Error in generating email: {e}")
        return None
    return output

def generateTelegram():
    sys_stats = getSysStats()

    info = {
        "title": PLUGIN_NAME,
        "system_uptime": sys_stats["system_uptime"],
        "node_uptime": sys_stats["node_uptime"],
        "node_version": getCurrentNodeVersion(),
        "latest_node_version": getLatestNodeVersion(),
        "cpu_utilization": sys_stats["node_cpu_usage"],
        "memory_utilization": sys_stats["node_memory_usage_mb"],
        "net_info": generateNetworkData()
    }

    template_setting = getConfigValue("webui", "template", default="cards")
    template_path = f"{template_setting}/telegram.html"
    try:
        logNotice(f"Generating Telegram message...")
        template = handlers.env.get_template(template_path)
        output = template.render(info)
    except Exception as e:
        logError(f"Error in generating Telegram message: {e}")
        return None
    return output
