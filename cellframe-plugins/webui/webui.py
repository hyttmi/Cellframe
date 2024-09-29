from pycfhelpers.node.http.simple import CFSimpleHTTPServer, CFSimpleHTTPRequestHandler
from concurrent.futures import ThreadPoolExecutor
from handlers import *
from utils import *
from generators import generateEmail
from mailer import sendMail
    
def HTTPServer():
    try:
        handler = CFSimpleHTTPRequestHandler(methods=["GET", "POST"], handler=requestHandler)
        CFSimpleHTTPServer().register_uri_handler(uri=f"/{PLUGIN_URI}", handler=handler)
        logNotice("started")
    except Exception as e:
        logError(f"Error: {e}")
    return 0

def init():
    email_stats_enabled = getConfigValue("webui", "email_stats")
    email_stats_time = getConfigValue("webui", "email_time")
    with ThreadPoolExecutor() as executor:
        executor.submit(HTTPServer)
        if email_stats_enabled and validateTime(email_stats_time):
            logNotice(f"Email sending is activated at time {email_stats_time}")
            executor.submit(funcScheduler, lambda: sendMail(generateEmail()), email_stats_time)
    return 0

def deinit():
    logNotice("stopped")
    return 0
