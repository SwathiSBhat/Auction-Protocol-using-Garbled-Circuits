from __future__ import print_function

import socket
import threading
from util.commitment import Double_Commitment
import random
import hashlib
import json
from util import *
import garbler_test
# import pickle
import os
# import sys

# variables
MAX_DATA_RECV = 999999
# flag to indicate presence of NOT gate as input gate in circuit
IS_NOT_GATE = 0
# tag corresponding to 1 in NOT gate
not_tag = None


class ProxyThread(threading.Thread):

    def __init__(self, proxyaddr, proxysock):
        threading.Thread.__init__(self)
        self.proxy_socket = proxysock
        print("New proxy connection made at: ", proxyaddr)

    def run(self):
        """
        VPOT
        """
        # creation of RSA modulus n by Sender i.e n=p*q
        pub_key, priv_key = GM.GM_keygen(12)
        N = pub_key[1]
        p, q = priv_key[0], priv_key[1]

        # --------- Initialization ---------
        TAGS = []
        C_RAND = []
        KEYS = []
        comm = []
        CO_all = []
        U = []
        U_str = []
        A = []
        c_list = []
        # ----------------------------------

        # 0. Send number of bidders to proxy
        # Proxy sends connection number to sender so that
        # sender can initialize corresponding tags
        data = json.dumps({"count": CONN_COUNT, "ip_len": ip_len})
        self.proxy_socket.send(data.encode())
        data = self.proxy_socket.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        # connection count received from proxy
        count = data.get("conn_count")
        print("Received CONNECTION {} from proxy", count)

        # 1. Sender chooses tags t0,t1 and an integer C
        for i in range(ip_len):
            tags = []
            try:
                last_index = (ip_len * count) - 1
                index = last_index - ip_len + 1 + i
                # print("index: ",index)
                t0 = mycirc.poss_inputs[index][0]
                t1 = mycirc.poss_inputs[index][1]
                # print("Tag0: {} Tag1: {}".format(t0,t1))
                tags.append(t0)
                tags.append(t1)
            except(IndexError):
                raise ValueError(
                    "Something went wrong with the inputs. Exiting...")
                os._exit(0)
            TAGS.append([t0, t1])

            while True:
                C = random.SystemRandom().randint(1, N-1)
                if util.gcd(C, N) == 1:
                    break
            C_RAND.append(C)

            # 2. Sender computes commitmentsand ordering a
            # Also computes u = E[a] and CO = Hash(u)
            # Transmit (C0,C1), CO to proxy
            a = random.SystemRandom().getrandbits(1)
            # print("a: ",a)
            A.append(a)
            # generating witnesses k0 and k1 for computing commitments
            k = []
            k.append(random.SystemRandom().randint(1, N-1))
            k.append(random.SystemRandom().randint(1, N-1))
            # DEBUG
            # print("k0: {} k1: {}".format(k[0],k[1]))
            KEYS.append(k)

            C0 = Double_Commitment(k[a], tags[a], N).commitment
            C1 = Double_Commitment(k[1-a], tags[1-a], N).commitment
            comm.append([C0, C1])

            u = GM.GM_encrypt(str(a), pub_key)
            u_str = ''.join(str(x) for x in u)
            CO = hashlib.sha256(u_str).hexdigest()
            U.append(u)
            U_str.append(u_str)
            CO_all.append(CO)

        data = json.dumps({"pub_key": pub_key, "C": C_RAND,
                           "comm": comm, "u": U, "CO": CO_all})
        print("-------------------------------------")
        print("Sent public_key:{}, commitment: {}, u: {}, CO:{} C:{} to proxy".format(
            pub_key, comm, U_str, CO_all, C_RAND))
        print("-------------------------------------")
        self.proxy_socket.send(data.encode())

        # 5. Sender receives x0 from proxy and computes x1=x0*C
        # y0 = x0^1/3 y1 = x1^1/3. Sender decrypts bs
        # if bs=0 transmit (z0,z1)=(y0k0,y1k1) to proxy else (y0k1,y1k0)
        # Send u to proxy

        v_list = []
        data = self.proxy_socket.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        x0, v = data.get("x0"), data.get("v")
        for i in v:
            v_list.append([int(i)])
        print("Received x0: {} v: {} from proxy".format(x0, v_list))
        print("-------------------------------------")

        bid_s = []
        Z0 = []
        Z1 = []
        for i in range(ip_len):
            x0[i] = x0[i] % N
            x1 = (x0[i]*C_RAND[i]) % N
            y = []
            y0 = cuberoot.cuberoot_util(x0[i], p, q)
            y1 = cuberoot.cuberoot_util(x1, p, q)
            # print("Cube root y0: ",y0," y1: ",y1)
            y.append(y0)
            y.append(y1)

            bs = int(GM.GM_decrypt(v_list[i], priv_key))
            print("Decrypted bs: ", bs)
            bid_s.append(bs)

            if bs == 0:
                z0, z1 = (y[0]*KEYS[i][0]) % N, (y[1]*KEYS[i][1]) % N
                # print("z0=y0k0: ",z0," z1=y1k1: ",z1)
            else:
                z0, z1 = (y[0]*KEYS[i][1]) % N, (y[1]*KEYS[i][0]) % N
                # print("z0=y0k1: ",z0," z1=y1k0: ",z1)
            Z0.append(z0)
            Z1.append(z1)

            # TODO : decommitting c to be done by proxy
            # Sender reveals c=a^bs by decommitting uv=E[a]E[bs]=E[c]
            # print("U: {} v_lsit: {}".format(U,v_list))
            uv = U[i][0]*v_list[i][0]
            uvlist = []
            uvlist.append(uv)
            c = GM.GM_decrypt(uvlist, priv_key)
            c_list.append(c)

        # if input circuit has NOT gate
        # send tag corresponding to 1 input directly to proxy
        if count == CONN_COUNT and IS_NOT_GATE == 1:
            data = json.dumps({"z0": Z0, "z1": Z1, "u": U_str,
                               "c": c_list, "not_tag": not_tag})
            print("Sent not_tag : {} to proxy".format(not_tag))
        else:
            data = json.dumps({"z0": Z0, "z1": Z1, "u": U_str, "c": c_list})
        self.proxy_socket.send(data.encode())
        print("Sent u: {} z0: {} z1: {} c:{} to proxy".format(
            u_str, z0, z1, c_list))

        # NOTE - Send c along with previous step since:
        # synchronization can cause problems in few cases
        # print("u[0]: {} type:u[0]: {} v: {} type(v): {}".format(u[0],type(u[0]),v,type(v)))
        print("-------------------------------------")


# *----- SENDER ------*

with open("test/circuit.json", 'r') as f:
    data = json.load(f)
data = json_util.byteify(data)

# ip_len = input length of each bid
ip_len = int(raw_input("Enter input length of bids: "))
num_inputs = data.get("num_inputs")
# if using example circuit 1 or circuit 3
# num_inputs = 4
# if using example circuit 2
# num_inputs = 5

if num_inputs % ip_len != 0:
    print("Inputs can't be distributed among bidders!")
    exit(0)
else:
    CONN_COUNT = num_inputs/ip_len
    print("CONN_COUNT: ", CONN_COUNT)

on_input_gates = data.get("on_input_gates")
mid_gates = data.get("mid_gates")
inter_gates = data.get("inter_gates")
output_gates = data.get("output_gates")


# example circuit 1
"""
on_input_gates = [[0, "AND", [0, 1]], 
                [1, "NOT", [1, 4]], 
                [2, "OR", [2, 3]]]

mid_gates = [[3, "OR", [0, 1]]]

inter_gates = []

output_gates = [[4, "AND", [2, 3]]]
"""
# example circuit 2
"""
on_input_gates = [[0, "AND", [0, 1]], 
                [1, "XOR", [1, 4]], 
                [2, "OR", [2, 3]]]

mid_gates = [[3, "OR", [0, 1]]]

inter_gates = []

output_gates = [[4, "AND", [2, 3]]]
"""
# example circuit 3 - Bigger(X,Y)
# X,Y = 2-bit integers
"""
on_input_gates = [[0, "NOT", [0, 4]],
                [1, "NOT", [2, 4]],
                [2, "NOT", [2, 4]],
                [3, "NOT", [3, 4]],
                [4, "NOT", [0, 2]]
                ]

mid_gates = [[5, "AND", [0, 1]],
            [8, "OR", [4, 5]],
            [9, "AND", [7, 8]]
            ]

inter_gates = [[6, "AND", [0, 2], [True, False]],
              [7, "AND", [1, 3], [True, False]]
            ]

output_gates = [[10, "OR", [6, 9]]]
"""


# checking for presence of NOT gate as input gate
for i in range(0, len(on_input_gates)):
    if on_input_gates[i][1] == "NOT":
        IS_NOT_GATE = 1
        break

if IS_NOT_GATE:
    # increase number of inputs to circuit
    mycirc = garbler_test.Circuit(
        num_inputs+1, on_input_gates, mid_gates, inter_gates, output_gates)
else:
    print("num_inputs : ", num_inputs)
    mycirc = garbler_test.Circuit(
        num_inputs, on_input_gates, mid_gates, inter_gates, output_gates)
print("Possible input tags: ", mycirc.poss_inputs)
print("----------------------------------------")

# garbled input corresponding to 1 in NOT gate
if IS_NOT_GATE:
    not_tag = mycirc.poss_inputs[-1][1]


# DEBUG
# with open('poss_ips.txt','w') as f:
#    pickle.dump(mycirc.poss_inputs,f)

"""
if mycirc.num_inputs != num_inputs:
    raise ValueError("Number of inputs to circuit and bidders don't match!")
    os._exit(0)    
"""
mycirc.prep_for_json()

sender_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# TODO  :make it dynamic
# sender_server.bind(('',0))
sender_server.bind(('127.0.0.1', 50000))

# allow sender server to spawn several threads when proxy connects with new client
print("Sender server started at : ", sender_server.getsockname())

while True:
    try:
        sender_server.listen(1)
        proxysock, proxyaddr = sender_server.accept()
        newthread = ProxyThread(proxyaddr, proxysock)
        newthread.start()
    except KeyboardInterrupt:
        print("Shutting down....")
        exit(0)
