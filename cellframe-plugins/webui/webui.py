from pycfhelpers.node.http.simple import CFSimpleHTTPServer, CFSimpleHTTPRequestHandler
from concurrent.futures import ThreadPoolExecutor
from handlers import *
from utils import *
    
def HTTPServer():
    try:
        handler = CFSimpleHTTPRequestHandler(methods=["GET", "POST"], handler=requestHandler)
        CFSimpleHTTPServer().register_uri_handler(uri=f"/{PLUGIN_URI}", handler=handler)
        logNotice("started")
    except Exception as e:
        logError(f"Error: {e}")
    return 0

def init():
    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(HTTPServer)
            return future.result()
    except Exception as e:
        logError(f"Error: {e}")
        return 0

def deinit():
    logNotice("stopped")
    return 0
