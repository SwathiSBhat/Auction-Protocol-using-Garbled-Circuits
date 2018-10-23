from __future__ import print_function

import socket
import threading
from util.commitment import Double_Commitment 
import random 
import hashlib 
import json 
from util import *
import garbler  
import os 
import pickle

#variables
MAX_DATA_RECV = 999999
# number of gc to generate for cut-n-choose
n = 5

class ProxyThread(threading.Thread):

    def __init__(self, proxyaddr, proxysock):
        threading.Thread.__init__(self)
        self.proxy_socket = proxysock
        print("New proxy connection made at: ", proxyaddr)

    def run(self):
        """
        VPOT
        """
        # ------------ TO BE DONE ONCE --------------

        # creation of RSA modulus n by Sender i.e n=p*q
        # TODO: make sure getting privkey is hard for others 
        with open('init.json') as f:
            data = json.load(f)
        pub_key,priv_key = data.get("pub_key"),data.get("priv_key")
        N = pub_key[1]
        p,q = priv_key[0],priv_key[1]
        A, indices = data.get("A"), data.get("indices")
        

        # 0. Send number of bidders to proxy 
        # Proxy sends connection number to sender so that
        # sender can initialize corresponding tags
        data = json.dumps({"count":CONN_COUNT})
        self.proxy_socket.send(data.encode())
        data = self.proxy_socket.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        # connection count received from proxy
        count = data.get("conn_count")
        print("Received conn_count {} from proxy".format(count)) 
        # TODO: Add method to end if count > CONN_COUNT
        if count > CONN_COUNT:
            print("Number of bidders can't be greater than number of inputs")
        print("---------------------------------")

        # -------------- END ---------------------------

        CIRCUITS = []
        TAGS = []
        C_RAND = []
        KEYS = []
        COMM = []
        k = []
        comm = []
        u_all = []
        commCO = []
        V = []
        X0 = []
        X1 = []
        Y = []
        Z = []
        c_list = []
        u_allstr = []
        
        # TODO: Check if indices range starts from 0 or 1
        full_list = [x for x in range(0,n)]
        indices = set(indices)
        indices_eval = list(indices^set(full_list))
        # print("indices recv: {} indices to eval: {}".format(indices,indices_eval))

        # CIRCUITS contains the circuits generated in offline step
        with open("circuit.data","rb") as f:
            CIRCUITS = pickle.load(f)
        # print("circuits : ",CIRCUITS)
        with open("key.data", "rb") as f:
            KEYS = pickle.load(f)
        # print("keys : ",KEYS)
        with open("comm.data", "rb") as f:
            COMM = pickle.load(f)
        # print("comm: ",COMM)
        
        # 1. Sender chooses tags t0,t1 and an integer C  
        # create tags, comm, keys for 1 bidder at a time
        # => 2 tags, 2 commitments, 2 keys
        for i in indices_eval:
            print("CONN_COUNT: ",count)
            try:
                t0 = CIRCUITS[i].poss_inputs[count-1][0]
                t1 = CIRCUITS[i].poss_inputs[count-1][1]
                print("Tag0: {} \n Tag1: {}".format(t0,t1))

                # DEBUG
                tag_int0 = gc_util.encode_str(t0)
                tag_int1 = gc_util.encode_str(t1)
                print("TagInt0: {} \n TagInt1: {}".format(tag_int0,tag_int1))
            
            except(IndexError):
                raise ValueError("Number of bidders can't be greater than no of inputs")
            TAGS.append([t0,t1])

            while True:
                C = random.SystemRandom().randint(1, N-1)
                if util.gcd(C, N) == 1:
                    break
            C_RAND.append(C)


            # 2. Sender computes commitments and ordering a
            # Also computes u = E[a] and CO = Hash(u)
            # Transmit (C0,C1), CO to proxy

            a = A[i][count-1]
            print("a: ",a)

            """
            k = []
            k.append(random.SystemRandom().randint(1,N-1))
            k.append(random.SystemRandom().randint(1,N-1))
            # DEBUG
            print("k0: {} k1: {}".format(k[0],k[1]))
            """
            k.append([KEYS[i][count-1][0], KEYS[i][count-1][1]])

            print("---------------------------")
            print("i: {}, count-1: {}".format(i,count-1))
            print("KEYS[0]:  {} KEYS[1]: {}".format(KEYS[i][count-1][0],KEYS[i][count-1][1]))

            C0 = COMM[i][count-1][0]
            C1 = COMM[i][count-1][1]
            comm.append([C0,C1])

            # DEBUG
            print("comm for circuit {}: {},{}".format(i,C0,C1))

            """
            C0 = Double_Commitment(k[a],t[a],N).commitment
            C1 = Double_Commitment(k[1-a],t[1-a],N).commitment
            """

            # TODO: u is a list returned by GM_encrypt
            u = GM.GM_encrypt(str(a),pub_key)
            u_str = ''.join(str(x) for x in u)
            CO = hashlib.sha256(u_str).hexdigest()
            commCO.append(CO)
            u_all.append(u)
            u_allstr.append(u_str) 

        print("Below printing values are for ONE BIDDER ONLY")
        print("---------------------------------")
        print("All tags for 3 circuits: ",TAGS)
        print("---------------------------------")
        print("All random Cs for 3 circuits: ",C_RAND)
        print("---------------------------------")
        print("All a for 3 circuits: ",A)
        print("---------------------------------")
        print("All keys for 3 circuits: ",k)
        print("---------------------------------")
        # print("All comm for 3 circuits: ",comm)
        # print("---------------------------------")
        print("All CO for 3 circuits: ",commCO)
        print("---------------------------------")
        print("All u for 3 circuits: ",u_all)
        
        data = json.dumps({"pub_key":pub_key, "C":C_RAND, "CO":commCO, "comm":comm, "u":u_allstr,"indices":indices_eval})
        print("-------------------------------------")
        print("Sent pub_key: {},  u: {}, CO:{}, indices:{} to proxy".format(pub_key,u_allstr,commCO,indices_eval))
        print("-------------------------------------")
        self.proxy_socket.send(data.encode())

        # TODO: Send bs directly from chooser
        # 5. Sender receives x0 from proxy and computes x1=x0*C
        # y0 = x0^1/3 y1 = x1^1/3. Sender decrypts bs
        # if bs=0 transmit (z0,z1)=(y0k0,y1k1) to proxy else (y0k1,y1k0)
        # Send u to proxy 
        # TODO : Check if v is also to be different for each circuit
        v_list = []
        data = self.proxy_socket.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        # X0 = list containing x0 for all circuits
        X0,v = data.get("x0"),data.get("v")
        v_list.append(int(v))
        print("Received x0: {} v: {} from proxy".format(X0,v_list))

        bs = int(GM.GM_decrypt(v_list,priv_key))
        print("Decrypted bs: ",bs," type(bs): ",type(bs))

        for i in range(0,len(indices_eval)):
            # TODO : check if this is required x0%N
            X0[i] = X0[i] % N
            X1.append((X0[i]*C_RAND[i])%N)
            # TODO: check if it is always a cube root
            # TODO: incorporate hardness to find cube root here
            y0 = cuberoot.cuberoot_util(X0[i],p,q)
            y1 = cuberoot.cuberoot_util(X1[i],p,q)
            print("Cube root y0: ",y0," y1: ",y1)
            Y.append([y0,y1])

            if bs==0:
                z0,z1 = (Y[i][0]*k[i][0])%N,(Y[i][1]*k[i][1])%N
                # print("z0=y0k0: ",z0," z1=y1k1: ",z1)
            else:
                z0,z1 = (Y[i][0]*k[i][1])%N,(Y[i][1]*k[i][0])%N
                # print("z0=y0k1: ",z0," z1=y1k0: ",z1)
            Z.append([z0,z1])
            
            # Sender reveals c=a^bs by decommitting uv=E[a]E[bs]=E[c]
            # print("u[0]: {} type:u[0]: {} v: {} type(v): {}".format(u[0],type(u[0]),v,type(v)))
            uv = u_all[i][0]*v_list[0]
            uvlist = []
            uvlist.append(uv)
            # print("uv_list: ",uvlist)
            c = GM.GM_decrypt(uvlist,priv_key)
            c_list.append(c)
        
        
        data = json.dumps({"Z":Z, "u":u_allstr, "c":c_list})
        self.proxy_socket.send(data.encode())
        print("Sent u: {} Z: {} c:{} to proxy".format(u_allstr,Z,c_list))
        print("-------------------------------------")
       

# *----- SENDER -----*

CONN_COUNT = int(raw_input("Enter number of bidders: "))

# TODO: Make entering of circuit from file or dynamic
on_input_gates = [[0, "AND", [0, 1]], 
                [1, "XOR", [2, 3]], 
                [2, "OR", [0,3]]]

mid_gates = [[3, "XOR", [0, 1]],
             [4, "OR", [1, 2]]]

output_gates = [[5, "OR", [3, 4]]]

CIRCUITS = []

"""
if os.path.isfile("testckt.json"):
    os.remove("testckt.json")

for i in range(0,5):
    mycirc = garbler.Circuit(4, on_input_gates, mid_gates, output_gates)
    # print("Possible input tags: ",mycirc.poss_inputs)
    # print("----------------------------------------")
 
    # TODO: Make this quit program
    if mycirc.num_inputs != CONN_COUNT:
        raise ValueError("Number of inputs to circuit and bidders don't match!")
    
    # TODO: Get CIRCUITS from offline step
    CIRCUITS.append(mycirc)
    filename = "testckt.json"
    mycirc.prep_for_json_cut_n_choose(filename)
"""

sender_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

# HOST = 127.0.0.1
# PORT = 50000
sender_server.bind(('127.0.0.1',50000))


# allow sender server to spawn several threads when proxy connects with new client
print("Sender server started at : ",sender_server.getsockname())

while True:
    sender_server.listen(1)
    proxysock, proxyaddr = sender_server.accept()
    newthread = ProxyThread(proxyaddr,proxysock)
    newthread.start()


