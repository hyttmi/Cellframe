from pycfhelpers.node.http.simple import CFSimpleHTTPServer, CFSimpleHTTPRequestHandler, CFSimpleHTTPResponse
from concurrent.futures import ThreadPoolExecutor

import base64
import utils
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("webui"),
    autoescape=select_autoescape()
)

def generateHtml():
    sys_stats = utils.getSysStats()
    is_update_available, curr_version, latest_version = utils.checkForUpdate()

    
    info = {
        'update_available': is_update_available,
        'current_version': curr_version,
        'latest_version': latest_version,
        "title": utils.PLUGIN_NAME,
        "hostname": utils.getHostname(),
        "external_ip": utils.getExtIP(),
        "system_uptime": sys_stats["system_uptime"],
        "node_uptime": sys_stats["node_uptime"],
        "node_version": utils.getCurrentNodeVersion(),
        "latest_node_version": utils.getLatestNodeVersion(),
        "networks": utils.getListNetworks(),
        "cpu_utilization": sys_stats["node_cpu_usage"],
        "memory_utilization": sys_stats["node_memory_usage_mb"],
        "header_text": utils.getConfigValue("webui", "header_text", default=False),
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
    utils.log_notice(f"Handling request from {request.client_address}...")
    if request.body:
        utils.log_notice(f"Received {request.body}")
    
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
    def task():
        try:
            handler = CFSimpleHTTPRequestHandler(methods=["GET", "POST"], handler=request_handler)
            CFSimpleHTTPServer().register_uri_handler(uri=f"/{utils.PLUGIN_URI}", handler=handler)
            utils.log_notice("started")
        except Exception as e:
            utils.log_error(f"Error: {e}")
        return 0
    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(task)
            return future.result()
    except Exception as e:
        utils.log_error(f"Error: {e}")
        return 0


def deinit():
    utils.log_notice("stopped")
    return 0
