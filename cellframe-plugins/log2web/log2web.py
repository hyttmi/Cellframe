from DAP.Network import ServerCore, HttpSimple
from DAP.Core import logIt, AppContext
from DAP import configGetItem
import os

plugin_name = "log2web"
version = "0.1"

def http_handler(sh, httpCode):
    log_file = configGetItem("resources", "log_file")
    if os.path.exists(log_file):
        f = open(log_file, "r")
        lines = f.readlines()
        for line in reversed(lines):
            sh.replyAdd(line.encode("utf-8"))
            httpCode.set(200)
        f.close()
    else:
        logIt.error("Can't find log file!")


def init():
    sc = ServerCore()
    AppContext.getServer(sc)
    HttpSimple.addProc(sc, "/logs", 96000, http_handler)
    logIt.notice(f"Plugin {plugin_name} v.{version} started...")
    return 0

def deinit():
    return