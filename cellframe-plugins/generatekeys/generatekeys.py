from DAP.Crypto import Algo
from DAP.Core import logIt
import time

def generateKeys():
    time.sleep(10) #Let's sleep for 10 secs before running the loop
    timestamp_start = time.perf_counter()
    amount = 500
    i = 0
    keytype = 14
    while i <= amount:
        Algo.generateNewKey(keytype, "supercalifragilisticexpialidocious", 512) 
        Algo.decodeBase64("supercalifragilisticexpialidocious", 2)
        i += 1
    timestamp_end = time.perf_counter()
    time_taken = timestamp_end - timestamp_start
    print(f"It took {time_taken:0.2f} seconds to generate {amount} keys and to do {amount} of decodeBase64 operations")
    logIt.notice("Done!")

def init():
    generateKeys()
    logIt.notice("Initializing generatekeys plugin")
    return 0