from __future__ import print_function

import socket
import json
import threading
import GM
import util 
import random
import gc_util

# variables
MAX_DATA_RECV = 999999

# asynchronous threads are needed, hence no thread locks required

SERVER = '127.0.0.1'
# PORT = int(raw_input("Enter proxy-server port number: "))
PORT = 50001

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER,PORT))

# TODO : Send indices
indices = [1,3,4]

"""
VPOT Protocol
"""
# b = int(raw_input("Enter your bit(0/1): "))

# DEBUG
b = 1

# 3. Chooser receives N,C from proxy and splits b into b = bs ^ bp
# Select x in Zn*. If bp=0 x0=x^3 else x0=x^3/C. Also compute v=E[bs]
data = client.recv(MAX_DATA_RECV)
data = json.loads(data.decode())
pub_key,C = data.get("pub_key"),data.get("C")
N = pub_key[1]
print("Received pub_key: {} , C: {} from proxy".format(pub_key,C))
print("---------------------------------------------")

bs = random.SystemRandom().getrandbits(1)
bp = b^bs

#bp = random.SystemRandom().getrandbits(1)
# DEBUG
# bs = 0
# bp = 0

print("bs:{}, bp:{}, b:{} ".format(bs,bp,b))

X0 = []
X = []

for i in range(0,len(indices)):
    while True:
        x = random.SystemRandom().randint(1,N-1)
        if util.gcd(x,N)==1:
            break 

    if bp == 0:
        x0 = (x*x*x)%N
    else:
        x0 = util.modular_div_util(pow(x,3),C[i],N)
    
    X0.append(x0)
    X.append(x)

v = GM.GM_encrypt(str(bs),pub_key)

# 4. Chooser sends (x0,v,x) to proxy. Proxy sends to sender: (x0,v)
v_str = ''.join(str(s) for s in v)
data = json.dumps({"x0":X0, "v":v_str, "x":X, "bp":bp})
print("Sent x0: {},v: {},x: {}, bp: {} to proxy".format(X0,v,X,bp))
client.send(data.encode())


# Receive tag_int from proxy
data = client.recv(MAX_DATA_RECV)
data = json.loads(data.decode())
tags = data.get("tag_all")
print("Received tag_all: {} from proxy".format(tags))


"""
end of VPOT
"""

"""
# TODO: check if 2048 is enough
while True:
    in_data = client.recv(2048)
    print("Recv from proxy-server: ",in_data.decode())
    if in_data.decode() == "quit":
        print("Quitting...")
        break
    try: 
        out_data = raw_input("Enter data to be sent to proxy: ")
        client.send(bytes(out_data))
        if out_data == "quit":
            break
    except KeyboardInterrupt:
        client.send(bytes("quit"))
        break
"""
print("Client closed")
client.close()




