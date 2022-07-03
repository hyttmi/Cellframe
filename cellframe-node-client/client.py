#!/usr/bin/python3
import socket
import sys

socket_path = "/opt/cellframe-node/var/run/node_cli"

print("Creating socket...")

try:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
except socket.error:
    print("Failed to create socket")
    sys.exit()
print("Connecting to server, " + socket_path)
s.connect(socket_path)

command = input("> ")
if command != "exit":    
    length = str(len(command))
    command = command.replace(" ", "\r\n")
    post = "POST /connect HTTP/1.1\r\nHost: localhost\r\nContent-Type: text/text\r\nContent-Length: " + length + "\r\n\r\n" + command + "\r\n\r\n"
    post = bytes(post,"utf-8")

    s.sendall(post)
    reply = s.recv(4096)
    reply = reply.decode("utf-8")
    reply = reply.split("\n")
    reply = list(filter(None, reply))
    reply = reply[4:]
    for replies in reply:
        print(replies)
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    sys.exit() # Exit this client because Node has a bug somewhere in socket connection and sending multiple commands won't work.