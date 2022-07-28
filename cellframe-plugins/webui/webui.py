import http.server
import os
import functions

from DAP.Core import logIt

port = 8000
filepath = os.path.abspath(os.path.dirname(__file__))


class WebUIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=filepath, **kwargs)

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("...".encode("utf-8"))


def init():
    server_address = ("", port)
    server = http.server.ThreadingHTTPServer(server_address, WebUIHandler)
    server.serve_forever()
    logIt.error("WebUI serving at port " + str(port))
    return 0

def deinit(): 
    return
