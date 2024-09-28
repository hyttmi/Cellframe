from utils import *
import base64, urllib
from pycfhelpers.node.http.simple import CFSimpleHTTPRequestHandler, CFSimpleHTTPResponse
from jinja2 import Environment, PackageLoader, select_autoescape    

env = Environment(
    loader=PackageLoader("webui"),
    autoescape=select_autoescape()
)
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
            response_body = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="refresh" content="0;url='/{PLUGIN_URI}'>
                <script type="text/javascript">
                    window.location.href = '/{PLUGIN_URI}';
                </script>
                <title>Redirecting...</title>
            </head>
            <body>
                <p>If you are not redirected automatically, follow this <a href='/{PLUGIN_URI}'</a>.</p>
            </body>
            </html>
            """.encode("utf-8")
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
    response_body = generateHTML()
    response_body = response_body.encode("utf-8")
    response = CFSimpleHTTPResponse(body=response_body, code=200)
    response.headers = {
        "Content-Type": "text/html"
    }
    logNotice("Sending response...")
    return response