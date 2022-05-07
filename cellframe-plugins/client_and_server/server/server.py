from DAP.Core import logIt
from CellFrame.Network import Service, ServiceUID

def requested(srv, usage_id, client_remote, data):
    return 0

def response_success(srv, usage_id, client_remote, data):
    return 0

def response_error(srv, usage_id, client_remote, data):
    return 0

def next_success(srv, usage_id, client_remote, data):
    return 0

def custom_data(srv, usage_id, client_remote, data):
    logIt.notice(f"[SERVER PLUGIN] Received data: " + data.decode("utf-8"))
    return data


def init():
    logIt.notice("[SERVER PLUGIN] Initializing server plugin...")
    ch_uid = ServiceUID(123)
    srv_object = Service(
        ch_uid,
        "py_service",
        requested,
        response_success,
        response_error,
        next_success,
        custom_data
    )
    return 0
