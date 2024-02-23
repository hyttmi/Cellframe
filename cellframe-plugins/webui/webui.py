import DAP
from DAP.Core import logIt

import subprocess, ipaddress, os, sys, utils, base64, multiprocessing
from http.server import BaseHTTPRequestHandler, HTTPServer
import utils
from jinja2 import Environment, PackageLoader, select_autoescape
env = Environment(
    loader=PackageLoader("webui"),
    autoescape=select_autoescape()
)

ALLOWED_IP_RANGES = ["0.0.0.0/0"]
PLUGIN_NAME = "Cellframe Masternode WebUI"

def get_config_value(section, key, default=None, cast=None):
    try:
        value = DAP.configGetItem(section, key)
        if cast is not None:
            value = cast(value)
        return value
    except ValueError:
        return default

def is_ip_allowed(client_ip):
    for allowed_range in ALLOWED_IP_RANGES:
        if ipaddress.ip_address(client_ip) in ipaddress.ip_network(allowed_range, strict=False):
            return True
    return False

def generateHtml():
    info = {
        "hostname": utils.getHostname(),
        "system_uptime": utils.getSystemUptime(),
        "node_uptime": utils.getNodeUptime(),
        "node_version": utils.getCurrentNodeVersion(),
        "latest_node_version": utils.getLatestNodeVersion(),
        "networks": utils.getListNetworks(),
        "cpu_utilization": utils.getCPUStats(),
        "memory_utilization": utils.getMemoryStats(),
        "net_info": utils.generateNetworkData()
    }

    template = env.get_template(f"template.html")
    output = template.render(info)
    return output

class MyRequestHandler(BaseHTTPRequestHandler):

    USERNAME = get_config_value("webui", "username", default=None)
    PASSWORD = get_config_value("webui", "password", default=None)

    def do_GET(self):
        client_ip = self.client_address[0]
        logIt.notice(f"({PLUGIN_NAME}) Connection from: {client_ip}")
        if not is_ip_allowed(client_ip):
            self.send_response(403)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Forbidden: You are not allowed to access this server.</h1>')
            return
        
        if self.USERNAME is not None and self.PASSWORD is not None:
            auth_header = self.headers.get('Authorization')
            if auth_header is None or not self.check_basic_auth(auth_header):
                self.send_response(401)
                self.send_header('WWW-Authenticate', 'Basic realm="Access to the server"')
                self.end_headers()
                self.wfile.write(b'<h1>Unauthorized</h1>')
                return

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        html_data = generateHtml()

        self.wfile.write(html_data.encode('utf-8'))
    
    def check_basic_auth(self, auth_header):
        auth_type, auth_data = auth_header.split(None, 1)
        if auth_type.lower() == 'basic':
            decoded_bytes = base64.b64decode(auth_data.encode('utf-8'))
            decoded_str = decoded_bytes.decode('utf-8')
            username, password = decoded_str.split(':', 1)
            return username == self.USERNAME and password == self.PASSWORD
        return False

def start_server():
    PORT = get_config_value("webui", "port", default=9999, cast=int)
    server = HTTPServer(('0.0.0.0', PORT), MyRequestHandler)
    try:
        server.serve_forever()
        logIt.notice(f"({PLUGIN_NAME}) started on port {str(PORT)}.")
    except Exception as e:
        logIt.error(f"({PLUGIN_NAME}) server startup failed: {e}.")

def init():
    server_process = multiprocessing.Process(target=start_server)
    server_process.start()
    return 0

def deinit():
    logIt.notice(f"{PLUGIN_NAME} stopped.")
    return 0

init()