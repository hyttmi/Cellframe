from time import sleep
from DAP.Core import logIt
from DAP import configGetItem
import os

max_size = 50000000 # Size in bytes, defaults ~50MB

def monitorLogfile():
    while True:
        sleep(10)
        path = configGetItem("resources", "log_file")
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size > max_size:
                os.remove(path)
                logIt.notice(f"{path} file removed because it's size exceeded {max_size} bytes.")

def init():
    monitorLogfile()
    logIt.notice("Initializing logfile remove plugin")
    return 0
