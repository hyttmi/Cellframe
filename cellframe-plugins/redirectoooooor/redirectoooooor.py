from DAP.Core import logIt
from DAP import configGetItem

import socket
import threading

plugin_name="redirectoooooor"
version="0.1"
port = 12345

def redirectData():
    node_socket_path = configGetItem("conserver", "listen_unix_socket_path")

    local_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    ext_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        local_socket.connect(node_socket_path)
        logIt.notice(f"{plugin_name}: Connected to local socket!") 
    except:
        logIt.error(f"{plugin_name}: Error connecting to local socket!") 

    ext_conn = False
    try:
        ext_socket.bind(("127.0.0.1", port))
        logIt.notice(f"{plugin_name}: Socket created!") 
        ext_conn = True
    except:
        logIt.error(f"{plugin_name}: Error creating socket!") 

    if ext_conn:
        ext_socket.listen()
        logIt.notice(f"{plugin_name}: External socket listening...")
        conn, addr = ext_socket.accept()
        logIt.notice(f"{plugin_name}: Client connected!")
        with conn:
            while True:
                fwd = conn.recv(1024)
                local_socket.sendall(fwd)
                data = local_socket.recv(1024)
                conn.sendto(data, addr)
                conn.close()

def init():
    logIt.notice(f"{plugin_name} version {version} started...")
    socketThread = threading.Thread(target=redirectData)
    socketThread.start()
    return 0

def deinit():
    return