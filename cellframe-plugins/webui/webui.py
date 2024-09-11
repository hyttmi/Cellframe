from pycfhelpers.node.http.simple import CFSimpleHTTPServer, CFSimpleHTTPRequestHandler, CFSimpleHTTPResponse
from concurrent.futures import ThreadPoolExecutor
import threading

import base64
import utils
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader(utils.PLUGIN_URI),
    autoescape=select_autoescape()
)

def generateHtml():
    info = {
        "title": utils.PLUGIN_NAME,
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

    template_setting = utils.getConfigValue("webui", "template", default="cards")
    template_path = f"{template_setting}/template.html"
    try:
        utils.log_notice(f"Generating HTML page...")
        template = env.get_template(template_path)
        output = template.render(info)
    except Exception as e:
        utils.log_error(f"Error in generating HTML: {e}")
        output = f"<h1>Got an error: {e}</h1>"
    return output

def generateHtml_async():
    with ThreadPoolExecutor() as executor:
        future = executor.submit(generateHtml)
        return future.result()

def request_handler(request: CFSimpleHTTPRequestHandler):
    utils.log_notice("Handling request...")
    
    headers = request.headers
    auth_header = headers.get('Authorization')
    
    expected_username = utils.getConfigValue("webui", "username")
    expected_password = utils.getConfigValue("webui", "password")
    
    if not expected_username or not expected_password:
        utils.log_error(f"Missing configuration in cellframe-node.cfg. Username or password is not set, plugin will be unavailable!")
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

    response_body = generateHtml_async()

    response_body = response_body.encode("utf-8")
    response = CFSimpleHTTPResponse(body=response_body, code=200)
    response.headers = {
        "Content-Type": "text/html"
    }
    
    utils.log_notice("Sending response...")
    return response

def init():
    handler = CFSimpleHTTPRequestHandler(methods=["GET"], handler=request_handler)
    CFSimpleHTTPServer().register_uri_handler(uri=f"/{utils.PLUGIN_URI}", handler=handler)
    return 0

def deinit():
    utils.log_notice("stopped")
    return 0
