from DAP.Core import logIt
from DAP import configGetItem

import socket
import threading
import os
import datetime

plugin_name="redirectoooooor"
version="0.1"
port = 12345
allowed = ["127.0.0.1", "localhost", "192.168.1.10"] # use external IP address if connecting remotely!

def redirectData():
    node_socket_path = configGetItem("conserver", "listen_unix_socket_path")

    ext_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        ext_socket.bind(("0.0.0.0", port))
        ext_socket.listen()
        logIt.notice(f"{plugin_name}: External socket listening on port {port}...")
    except:
        logIt.error("Failed to bind external socket! Port in use?")

    while True:
        local_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        ext_conn, addr = ext_socket.accept()
        if addr[0] not in allowed:
            logIt.error(f"{plugin_name}: IP address is not allowed!")
            ext_conn.close()
            continue
        logIt.notice(f"{plugin_name}: Client connected from {addr}!")
        fwd_data = b''
        while True:
            fwd = ext_conn.recv(4096)
            fwd_data += fwd
            if len(fwd) < 4096:
                break
        fwd_str = fwd_data.decode("utf-8")
        fwd_str = fwd_str.replace("\r\n", " ")
        logIt.notice(f"{plugin_name}: Received data: {fwd_str}")
        try:
            local_socket.connect(node_socket_path)
            logIt.notice(f"{plugin_name}: Connected to local socket!")
        except:
            logIt.error(f"{plugin_name}: Connection to local socket failed!")
        local_socket.sendall(fwd_data)
        rcv_data = b''
        while True:
            data = local_socket.recv(4096)
            rcv_data += data
            if len(data) < 4096:
                break
        ext_conn.sendto(rcv_data, addr)
        ext_conn.close()
        local_socket.close()

def init():
    logIt.notice(f"{plugin_name} version {version} started...")
    socketThread = threading.Thread(target=redirectData)
    socketThread.start()
    return 0

def deinit():
    return