from pycfhelpers.node.http.simple import CFSimpleHTTPServer, CFSimpleHTTPRequestHandler
import threading
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
    http_thread = threading.Thread(target=HTTPServer)
    http_thread.start()
    if email_stats_enabled and validateTime(email_stats_time):
        logNotice(f"Email sending is activated at time {email_stats_time}")
        scheduler_thread = threading.Thread(target=funcScheduler, args=(lambda: sendMail(generateEmail()), email_stats_time))
        scheduler_thread.start()
    return 0

def deinit():
    logNotice("stopped")
    return 0
