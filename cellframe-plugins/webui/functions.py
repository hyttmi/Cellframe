import socket
from time import sleep
import json

def doSocketConnection():
    connected = False
    try:
        while not connected:
            socket_path = "/opt/cellframe-node/var/run/node_cli"
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(socket_path)
            connected = True
    except:
        sleep(10)

    return s, connected

def sendCommand(command):
    s, connected = doSocketConnection()
    if connected:
        length = str(len(command))
        command = command.replace(" ", "\r\n")
        post = "POST /connect HTTP/1.1\r\nHost: localhost\r\nContent-Type: text/text\r\nContent-Length: " + length + "\r\n\r\n" + command + "\r\n\r\n"
        post = bytes(post,"utf-8")
        s.sendall(post)
        reply = s.recv(65536)
        reply = reply.decode("utf-8")
        reply = reply.split("\n")
        reply = list(filter(None, reply))
        reply = reply[4:]
        s.shutdown(socket.SHUT_RDWR)
        s.close()

    return json.dumps(reply)