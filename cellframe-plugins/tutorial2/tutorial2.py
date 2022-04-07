import API_CellFrame as CF

def getwalletBalance(address):
    if len(address) != 104:
        data = "Provided address is wrong! Address length should be 104 characters, provided address has " + str(len(address)) + " characters!"
        data += "\n\n" 
        return data
    addr = CF.ChainAddr.fromStr(address)
    net_id = addr.getNetId()
    chain_net =  CF.ChainNet.byId(net_id)
    ledger = chain_net.getLedger()
    tokens =  ledger.addrGetTokenTickerAllFast(addr)
    if len(tokens) > 0:
        for token in tokens:
            balance = ledger.calcBalance(addr, token)
            data =  "\nAddress:\t" + str(addr)
            data += "\nToken:\t\t" + str(token)
            data += "\nBalance:\t" + str(balance[0])
            data += "\nDatoshi:\t" + str(balance[1])
            data += "\n\n"
            return data
    else:
        data = "Provided address is empty!"
        data += "\n\n"
        return data
    return

def http_handler(sh, httpCode):
    wallet = sh.query.split("?")
    if wallet:
        for wallets in wallet:
            wallets = wallets.split(" ", 1) # Remove the extra " HT" from the end
            wallets = wallets[0]
            CF.logItNotice("Getting wallet info for " + wallets)
            ret_str = getwalletBalance(wallets)
            sh.replyAdd(ret_str.encode("utf-8"))
            httpCode.set(200)

def init():
    sc = CF.ServerCore()
    CF.AppContext.getServer(sc)
    CF.HttpSimple.addProc(sc, "/wallet", 96000, http_handler)
    CF.logItNotice("Webserver started")
    return 0

def deinit():
    return