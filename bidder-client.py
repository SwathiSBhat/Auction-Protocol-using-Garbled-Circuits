#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : bidder-client.py
# Author            : Swathi S Bhat
# Date              : 07.12.2018
# Last Modified Date: 09.12.2018
# Last Modified By  : Swathi S Bhat
from __future__ import print_function

import socket
import json
import threading
from util import *
import random
import os 

# variables
MAX_DATA_RECV = 999999

# asynchronous threads are needed, hence no thread locks required

"""
VPOT Protocol
"""


def vpot_client():

    # 3. Chooser receives N,C from proxy and splits b into b = bs ^ bp
    # Select x in Zn*. If bp=0 x0=x^3 else x0=x^3/C. Also compute v=E[bs]
    data = client.recv(MAX_DATA_RECV)
    data = json.loads(data.decode())
    pub_key, C = data.get("pub_key"), data.get("C")
    N = pub_key[1]
    ip_len = data.get("ip_len")

    while True:
        try:
            b = int(raw_input("Enter bid: "))
            if b <= (pow(2, ip_len) - 1):
                b_bin = util.int_to_bin(b, ip_len)
                break 
            else:
                print("Bid value greater than input length. Try again.")
        except ValueError:
            print("ValueError - Invalid bid value")
            exit(0)
    
    print("Received pub_key: {} , C: {} from proxy".format(pub_key, C))
    print("-------------------------------------------")

    bid = []
    bid_s = []
    bid_p = []
    for i in b_bin:
        bs = random.SystemRandom().getrandbits(1)
        bp = int(i) ^ bs
        bid.append(int(i))
        bid_s.append(bs)
        bid_p.append(bp)

    print("bs:{}, bp:{}, b:{} ".format(bid_s, bid_p, bid))
    print("-------------------------------------------")

    X = []
    X0 = []
    V = []
    for i in range(ip_len):
        while True:
            x = random.SystemRandom().randint(1, N-1)
            if util.gcd(x, N) == 1:
                break

        if bid_p[i] == 0:
            x0 = pow(x, 3, N)
        else:
            x0 = util.modular_div_util(pow(x, 3), C[i], N)

        v = GM.GM_encrypt(str(bid_s[i]), pub_key)

        # 4. Chooser sends (x0,v,x) to proxy. Proxy sends to sender: (x0,v)
        v_str = ''.join(str(s) for s in v)

        X.append(x)
        X0.append(x0)
        V.append(v_str)

    data = json.dumps({"x0": X0, "v": V, "x": X, "bp": bid_p})
    print("Sent x0: {},v: {},x: {}, bp: {} to proxy".format(X0, V, X, bid_p))
    print("-------------------------------------------")
    client.send(data.encode())

    # Receive tag_int from proxy
    data = client.recv(MAX_DATA_RECV)
    data = json.loads(data.decode())
    tag_int = data.get("tag_int")
    # print("Received tag_int: {} from proxy".format(tag_int))

    for t in tag_int:
        tag = gc_util.decode_str(t)
        print("Decoded tag: ", tag)
    print("-------------------------------------------")

    """
    end of VPOT
    """


if __name__ == "__main__":
    try:
        SERVER = '127.0.0.1'
        # TODO : make it dynamic
        #PORT = int(raw_input("Enter proxy-server port number: "))
        PORT = 50001

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((SERVER, PORT))
            try:
                vpot_client()
            except ValueError:
                print("JSON Error")
                os._exit(0)
        except socket.error as e:
            print("An error occurred : ", e)
            exit(0)
    except(KeyboardInterrupt):
        print("\nShutting down...")
        exit(0)
