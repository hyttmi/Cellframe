import http.server
import os
from functions import *

from DAP.Core import logIt

port = 8000
filepath = os.path.abspath(os.path.dirname(__file__))


class WebUIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=filepath, **kwargs)

    def do_POST(self):
        length = int(self.headers.get_all('content-length')[0])
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        data_string = self.rfile.read(length)
        data_string = data_string.decode("utf-8")
        data = sendCommand(data_string)
        self.wfile.write(data.encode("utf-8"))


def init():
    logIt.message("WebUI serving at port " + str(port))
    server_address = ("0.0.0.0", port)
    server = http.server.ThreadingHTTPServer(server_address, WebUIHandler)
    server.serve_forever()
    return 0

def deinit(): 
    return
