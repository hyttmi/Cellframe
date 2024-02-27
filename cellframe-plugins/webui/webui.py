import DAP
from DAP.Core import logIt

import utils, base64, multiprocessing
from http.server import BaseHTTPRequestHandler, HTTPServer
import utils
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("webui"),
    autoescape=select_autoescape()
)

def generateHtml():
    info = {
        "hostname": utils.getHostname(),
        "external_ip": utils.getExtIP(),
        "system_uptime": utils.getSystemUptime(),
        "node_uptime": utils.getNodeUptime(),
        "node_version": utils.getCurrentNodeVersion(),
        "latest_node_version": utils.getLatestNodeVersion(),
        "networks": utils.getListNetworks(),
        "cpu_utilization": utils.getCPUStats(),
        "memory_utilization": utils.getMemoryStats(),
        "net_info": utils.generateNetworkData()
    }

    template_setting = utils.get_config_value("webui", "template", default="cards")
    template_path = f"{template_setting}/template.html"
    try:
        template = env.get_template(template_path)
        output = template.render(info)
    except Exception:
        output = f"<h1>Error: Template {template_path} not found</h1>"

    return output
        

class MyRequestHandler(BaseHTTPRequestHandler):

    USERNAME = utils.get_config_value("webui", "username", default=None)
    PASSWORD = utils.get_config_value("webui", "password", default=None)

    def do_GET(self):
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
    PORT = utils.get_config_value("webui", "port", default=9999, cast=int)
    server = HTTPServer(('0.0.0.0', PORT), MyRequestHandler)
    try:
        server.allow_reuse_address = True
        server.serve_forever()
    except Exception as e:
        logIt.error(f"(Cellframe Masternode WebUI) server startup failed: {e}.")
    finally:
        logIt.notice(f"(Cellframe Masternode WebUI) started on port {str(PORT)}.")

def init():
    server_process = multiprocessing.Process(target=start_server)
    server_process.start()
    return 0

def deinit():
    logIt.notice(f"(Cellframe Masternode WebUI) stopped.")
    return 0