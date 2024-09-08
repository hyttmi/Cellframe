from threading import Thread
from DAP.Core import logIt, AppContext
from DAP.Network import HttpSimple, Server, HttpHeader, HttpCode
import base64
import utils
from jinja2 import Environment, PackageLoader, select_autoescape

PLUGIN_NAME = "[Cellframe system & node info by Mika H (@CELLgainz)]"
PLUGIN_URI = "webui"
HTTP_REPLY_SIZE_MAX = 10 * 1024 * 1024

env = Environment(
    loader=PackageLoader(PLUGIN_URI),
    autoescape=select_autoescape()
)

def generateHtml():
    info = {
        "title": PLUGIN_NAME,
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
        template = env.get_template(template_path)
        output = template.render(info)
    except Exception as e:
        output = f"<h1>Got an error: {e}</h1>"
    return output

def http_handler(request: HttpSimple, httpCode: HttpCode):
    username = utils.getConfigValue("webui", "username")
    password = utils.getConfigValue("webui", "password")

    if not username or not password:
        request.replyAdd(b"Missing configuration in cellframe-node.cfg. Username or password is not set, plugin will be unavailable!")
        httpCode.set(200)
        return

    auth_header = next((header.value for header in request.requestHeader if header.name.lower() == 'authorization'), None)

    if not auth_header or not auth_header.startswith('Basic '):
        request.setResponseHeader(HttpHeader("WWW-Authenticate", 'Basic realm="Cellframe node WebUI"'))
        request.replyAdd(b"401 Unauthorized")
        httpCode.set(401)
        return

    try:
        credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
        req_username, req_password = credentials.split(':', 1)
    except Exception as e:
        logIt.error(f"{PLUGIN_NAME} Error decoding credentials: {e}")
        request.setResponseHeader(HttpHeader("WWW-Authenticate", 'Basic realm="Cellframe node WebUI"'))
        request.replyAdd(b"401 Unauthorized")
        httpCode.set(401)
        return

    if req_username != username or req_password != password:
        request.setResponseHeader(HttpHeader("WWW-Authenticate", 'Basic realm="Cellframe node WebUI"'))
        request.replyAdd(b"401 Unauthorized")
        httpCode.set(401)
        return

    try:
        html_content = generateHtml()
        request.replyAdd(html_content.encode('utf-8'))
        request.setResponseHeader(HttpHeader("Content-type", "text/html"))
        httpCode.set(200)
    except Exception as e:
        logIt.error(f"{PLUGIN_NAME} Error generating HTML: {e}")
        request.replyAdd(b"500 Internal Server Error")
        httpCode.set(500)

def http_proc_in_thread(server_instance):
    HttpSimple.addProc(server_instance, f"/{PLUGIN_URI}", HTTP_REPLY_SIZE_MAX, http_handler)

def init():
    server_instance = Server()
    AppContext.getServer(server_instance)
    proc_thread = Thread(target=http_proc_in_thread, args=(server_instance,))
    proc_thread.start()
    return 0

def deinit():
    logIt.notice(f"{PLUGIN_NAME} stopped.")
    return 0
