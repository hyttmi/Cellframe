from DAP.Core import logIt

import subprocess, ipaddress, os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import html_gen

ALLOWED_IP_RANGES = ["0.0.0.0/0"]
PORT = 9999
PLUGIN_NAME = "Cellframe Masternode WebUI"

def is_ip_allowed(client_ip):
    for allowed_range in ALLOWED_IP_RANGES:
        if ipaddress.ip_address(client_ip) in ipaddress.ip_network(allowed_range, strict=False):
            return True
    return False

class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]
        logIt.notice(f"Connection from: {client_ip}")
        if not is_ip_allowed(client_ip):
            self.send_response(403)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Forbidden: You are not allowed to access this server.</h1>')
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        html_data = html_gen.generateHtml()

        self.wfile.write(html_data.encode('utf-8'))

def start_server_in_thread():
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
