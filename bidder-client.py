from __future__ import print_function

import socket
import json
import threading
from util import *
import random

# variables
MAX_DATA_RECV = 999999

# asynchronous threads are needed, hence no thread locks required


"""
VPOT Protocol
"""
def vpot_client():
    try:
        # TODO - check for 0/1 only
        b = int(raw_input("Enter your bit(0/1): "))
    except ValueError:
        print("ValueError - Please enter a bit (0/1)")
        exit(0)
    
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

    print("bs:{}, bp:{}, b:{} ".format(bs,bp,b))

    while True:
        x = random.SystemRandom().randint(1,N-1)
        if util.gcd(x,N)==1:
            break 

    if bp == 0:
        x0 = (x*x*x)%N
    else:
        x0 = util.modular_div_util(pow(x,3),C,N)

    v = GM.GM_encrypt(str(bs),pub_key)

    # 4. Chooser sends (x0,v,x) to proxy. Proxy sends to sender: (x0,v)
    v_str = ''.join(str(s) for s in v)
    data = json.dumps({"x0":x0, "v":v_str, "x":x, "bp":bp})
    print("Sent x0: {},v: {},x: {}, bp: {} to proxy".format(x0,v,x,bp))
    client.send(data.encode())


    # Receive tag_int from proxy
    data = client.recv(MAX_DATA_RECV)
    data = json.loads(data.decode())
    tag_int = data.get("tag_int")
    print("Received tag_int: {} from proxy".format(tag_int))
    tag = gc_util.decode_str(tag_int)
    print("Decoded tag: ",tag)

    """
    end of VPOT
    """

if __name__ == "__main__":
    try:
        SERVER = '127.0.0.1'
        PORT = int(raw_input("Enter proxy-server port number: "))

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((SERVER,PORT))
            vpot_client()
        except socket.error as e:
            print("An error occurred : ",e)
            exit(0)
    except(KeyboardInterrupt):
        print("\nShutting down...")
        exit(0)

