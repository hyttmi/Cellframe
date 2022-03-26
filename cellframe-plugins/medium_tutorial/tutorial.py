import API_CellFrame as CF

def helloWorld(arg, strReply):
    reply = "Hello World!"
    CF.AppCliServer.setReplyText(reply, strReply)

def init():
    CF.AppCliServer.cmdItemCreate("helloworld", helloWorld, "Hello world command",
    "Simple plugin which prints \"Hello World!\" to the console.")
    return 0

def deinit():
    return