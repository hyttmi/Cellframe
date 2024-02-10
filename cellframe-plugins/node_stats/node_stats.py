from DAP.Core import logIt

import subprocess, ipaddress, os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import threading

ALLOWED_IP_RANGES = ["192.168.1.0/24", "10.0.0.0/8", "127.0.0.1"]  # Add the allowed IP ranges here
PORT = 9999
SCRIPT_PATH = f"{os.path.dirname(os.path.realpath(__file__))}/node_stats"

def is_ip_allowed(client_ip):
    for allowed_range in ALLOWED_IP_RANGES:
        if ipaddress.ip_address(client_ip) in ipaddress.ip_network(allowed_range, strict=False):
            return True
    return False

def run_shell_script(script_path):
    try:
        output = subprocess.check_output(['bash', script_path], stderr=subprocess.STDOUT, text=True)
        return output
    except subprocess.CalledProcessError as e:
        return f"Error running script: {e}"

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
        
        if not os.path.exists(SCRIPT_PATH):
            try:
                logIt.notice("Can't find node_stats script. Downloading latest...")
                url = 'https://raw.githubusercontent.com/hyttmi/Cellframe/main/cellframe-community/Nocdem/node_stats'
                destination = SCRIPT_PATH
                urllib.request.urlretrieve(url, destination)
            except Exception as e:
                logIt.error(f"Fetching latest node_stats failed with error: {e}")
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>Fetching latest node_stats failed, please try again.</h1>')
                return

        script_output = run_shell_script(SCRIPT_PATH)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(script_output.encode('utf-8'))

def start_server_in_thread():
    if os.path.exists(SCRIPT_PATH):
        logIt.notice(f"{SCRIPT_PATH} found, removing it...")
        os.remove(SCRIPT_PATH)

    server = HTTPServer(('0.0.0.0', PORT), MyRequestHandler)
    server.serve_forever()
    logIt.notice(f"Server started on port {PORT}.")

def init():
    server_thread = threading.Thread(target=start_server_in_thread)
    server_thread.start()
    return 0
