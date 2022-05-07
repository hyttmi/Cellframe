from DAP.Core import logIt
from CellFrame.Network import Net, ServiceUID, ServiceClient
from CellFrame import AppCliServer

def clientConnect(args, reply):
    if len(args) == 2:
        if args[0] == "clientplugin":
            if args[1] == "connect":
                net = Net.byName("subzero")
                client = ServiceClient(net, "127.0.0.1", 8079, callback_connected,
                                                               callback_disconnected,
                                                               callback_deleted,
                                                               callback_check,
                                                               callback_sign,
                                                               callback_success,
                                                               callback_error,
                                                               callback_data,
                                                               0)
                AppCliServer.setReplyText("Client connected to the server!", reply)
            else:
                AppCliServer.setReplyText("[CLIENT PLUGIN] Command usage: clientplugin connect", reply)
                logIt.error("[CLIENT PLUGIN] Command usage: clientplugin connect")
        else:
            AppCliServer.setReplyText("[CLIENT PLUGIN] Command usage: clientplugin connect")
            logIt.error("[CLIENT PLUGIN] Command usage: clientplugin connect")
    else:
        AppCliServer.setReplyText("[CLIENT PLUGIN] Command usage: clientplugin connect", reply)
        logIt.error("[CLIENT PLUGIN] Command usage: clientplugin connect")

def callback_connected(serviceClient, arg):
    logIt.notice("[CLIENT PLUGIN] Client connected...")
    ch_uid = ServiceUID(123)
    data = "This function is now called with command!"
    serviceClient.write(ch_uid, data.encode('utf-8'))
    logIt.notice(f"[CLIENT PLUGIN] sent data: {data}")

def callback_disconnected(serviceClient, arg):
    logIt.notice("[CLIENT PLUGIN] Python client disconnected")

def callback_deleted(serviceClient, arg):
    return 0

def callback_check(serviceClient, arg):
    return 0

def callback_sign(serviceClient, txCondRec, arg):
    return 0

def callback_success(serviceClient, txCondHash, arg):
    return 0

def callback_error(serviceClient, errorNum, arg):
    return 0

def callback_data(serviceClient, data, arg):
    logIt.notice(f"[CLIENT PLUGIN] Received from server plugin: {data.decode('utf-8')}")

def init():
    logIt.notice("[CLIENT PLUGIN] Initializing client plugin...")
    AppCliServer.cmdItemCreate("clientplugin",
                            clientConnect, "Connect to server plugin",
                            "With this command you can connect to the server plugin.")
    return 0