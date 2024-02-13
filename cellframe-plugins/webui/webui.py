import DAP
from DAP.Core import logIt

import subprocess, ipaddress, os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import html_gen
import base64

ALLOWED_IP_RANGES = ["0.0.0.0/0"]
PLUGIN_NAME = "Cellframe Masternode WebUI"

def get_config_value(section, key, default=None, cast=None):
    try:
        value = DAP.configGetItem(section, key)
        if cast is not None:
            value = cast(value)
        return value
    except (ValueError, KeyError):
        return default

def is_ip_allowed(client_ip):
    for allowed_range in ALLOWED_IP_RANGES:
        if ipaddress.ip_address(client_ip) in ipaddress.ip_network(allowed_range, strict=False):
            return True
    return False

class MyRequestHandler(BaseHTTPRequestHandler):

    USERNAME = get_config_value("webui", "username", default=None)
    PASSWORD = get_config_value("webui", "password", default=None)

    def do_GET(self):
        client_ip = self.client_address[0]
        logIt.notice(f"Connection from: {client_ip}")
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

        html_data = html_gen.generateHtml()

        self.wfile.write(html_data.encode('utf-8'))
    
    def check_basic_auth(self, auth_header):
        auth_type, auth_data = auth_header.split(None, 1)
        if auth_type.lower() == 'basic':
            decoded_bytes = base64.b64decode(auth_data.encode('utf-8'))
            decoded_str = decoded_bytes.decode('utf-8')
            username, password = decoded_str.split(':', 1)
            return username == self.USERNAME and password == self.PASSWORD
        return False

def start_server_in_thread():
    PORT = get_config_value("webui", "port", default=9999, cast=int)
    server = HTTPServer(('0.0.0.0', PORT), MyRequestHandler)
    try:
        server.serve_forever()
        logIt.notice(f"({PLUGIN_NAME}) started on port {str(PORT)}.")
    except Exception as e:
        logIt.notice(f"Server startup failed: {e}.")

def init():
    server_thread = threading.Thread(target=start_server_in_thread)
    server_thread.start()
    return 0

def deinit():
    logIt.notice(f"{PLUGIN_NAME} stopped.")
    return 0
