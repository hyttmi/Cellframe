from pycfhelpers.node.http.simple import CFSimpleHTTPServer, CFSimpleHTTPRequestHandler, CFSimpleHTTPResponse
from concurrent.futures import ThreadPoolExecutor

import base64, urllib, ssl
from utils import *
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("webui"),
    autoescape=select_autoescape()
)

def generateHtml():
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
        "link_key": getConfigValue("webui", "link_key", default=False),
        "net_info": generateNetworkData()
    }

    template_setting = getConfigValue("webui", "template", default="cards")
    template_path = f"{template_setting}/template.html"
    try:
        logNotice(f"Generating HTML page...")
        template = env.get_template(template_path)
        output = template.render(info)
    except Exception as e:
        logError(f"Error in generating HTML: {e}")
        output = f"<h1>Got an error: {e}</h1>"
    return output

def generateHtmlAsync():
    with ThreadPoolExecutor() as executor:
        future = executor.submit(generateHtml)
        return future.result()
    
def requestHandler(request: CFSimpleHTTPRequestHandler):
    if request.method == "GET":
        return getRequestHandler(request)
    elif request.method == "POST":
        return postRequestHandler(request)
    else:
        logError(f"Unsupported method: {request.method}")
        response = CFSimpleHTTPResponse(body=b"Unsupported method", code=200)
        return response
    
def postRequestHandler(request: CFSimpleHTTPRequestHandler):
    logNotice(f"Handling request from {request.client_address}...")
    if request.body:
        post_data = urllib.parse.parse_qs(request.body.decode('utf-8'))
        post_network = post_data["network"][0]
        parts = post_network.split("_")
        if len(parts) == 3:
            link_key, network, state = parts
        else:
            logError(f"Invalid format, got {post_network}")
            response = CFSimpleHTTPResponse(body=b"Invalid format!", code=200)
            return response
        if getConfigValue("webui", "link_key") == link_key:
            logNotice("Link key is correct, proceeding...")
            setNetworkState(state, network)
            response_body = b"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="refresh" content="0;url=/webui">
                <script type="text/javascript">
                    window.location.href = '/webui';
                </script>
                <title>Redirecting...</title>
            </head>
            <body>
                <p>If you are not redirected automatically, follow this <a href="/webui">link</a>.</p>
            </body>
            </html>
            """
            response = CFSimpleHTTPResponse(body=response_body, code=200)
            response.headers = {
            "Content-Type": "text/html"
            }
            return response
        else:
            response = CFSimpleHTTPResponse(body=b"Link key mismatch, action is prohibited!", code=200)
            logError("Link key mismatch, action is prohibited!")
            return response

def getRequestHandler(request: CFSimpleHTTPRequestHandler):
    logNotice(f"Handling request from {request.client_address}...")
    headers = request.headers
    auth_header = headers.get('Authorization')
    expected_username = getConfigValue("webui", "username")
    expected_password = getConfigValue("webui", "password")
    if not expected_username or not expected_password:
        logError(f"Missing configuration in cellframe-node.cfg. Username or password is not set, plugin will be unavailable!")
        response = CFSimpleHTTPResponse(body=b"Missing configuration in cellframe-node.cfg. Username or password is not set, plugin will be unavailable!", code=200)
        return response
    if not auth_header or not auth_header.startswith('Basic '):
        response = CFSimpleHTTPResponse(body=b"Unauthorized", code=401)
        response.headers = {
            "Content-Type": "text/plain",
            "WWW-Authenticate": 'Basic realm="Cellframe node webui"'
        }
        return response
    try:
        encoded_credentials = auth_header.split(' ', 1)[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':', 1)
    except (IndexError, ValueError):
        response = CFSimpleHTTPResponse(body=b"Unauthorized", code=401)
        response.headers = {
            "Content-Type": "text/plain",
            "WWW-Authenticate": 'Basic realm="Cellframe node webui"'
        }
        return response
    if username != expected_username or password != expected_password:
        response = CFSimpleHTTPResponse(body=b"Unauthorized", code=401)
        response.headers = {
            "Content-Type": "text/plain",
            "WWW-Authenticate": 'Basic realm="Cellframe node webui"'
        }
        return response
    response_body = generateHtmlAsync()
    response_body = response_body.encode("utf-8")
    response = CFSimpleHTTPResponse(body=response_body, code=200)
    response.headers = {
        "Content-Type": "text/html"
    }
    logNotice("Sending response...")
    return response
    
def task():
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
            future = executor.submit(task)
            return future.result()
    except Exception as e:
        logError(f"Error: {e}")
        return 0

def deinit():
    logNotice("stopped")
    return 0
