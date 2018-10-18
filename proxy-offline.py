from __future__ import print_function

import socket
import os
import sys
import json 
import thread
import threading 
import hashlib
import util 
import gc_util 
import evaluator
import random
import pickle 

# variables
BACKLOG = 50
MAX_DATA_RECV = 999999

# config of sender-server
SERVER = '127.0.0.1'
PORT = int(raw_input("Enter sender-server port number: "))

# TODO set n to practical value
n = 5

class ClientThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        # create a socket to connect to sender/server from proxy
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER,PORT))

        # --------- TO BE DONE ONCE ---------

        # Receive CONN_COUNT from sender
        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        CONN_COUNT = data.get("CONN_COUNT")

        # send inputs for which commitments are needed
        inputs = []
        for i in range(0,CONN_COUNT):
            inputs.append(random.SystemRandom().getrandbits(1))
        print("Inputs to circuits: ",inputs)
        data = json.dumps({"inputs":inputs})
        s.send(data.encode())
        
        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        pub_key,C = data.get("pub_key"),data.get("C")
        print("Received pub_key {} and C {} from sender".format(pub_key,C))
        N = pub_key[1]

        # --------- END ------------

        """
        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        COMM = data.get("COMM")
        # print("Commitments received: ",COMM)
        """

        # ---------- DEBUG -------------
        """
        print("--------------------------------")
        count_comm = 0
        for i in range(0,n):
            for j in range(0,len(inputs)):
                if COMM[i][j][0] == Comm[i][j][inputs[j]][0]:
                    print("Verified")
                    count_comm += 1
        print("Verified counts ( ideal = 20 ): ",count_comm)
        print("--------------------------------")
        """
        # ---------- END OF DEBUG ---------

        # TODO: change sampling range to number of circuits
        # TODO: Send number of circuits = n from sender to proxy
        num_of_indices = n/2
        # indices = indices of chosen circuits to open
        indices = random.SystemRandom().sample(range(0,n), num_of_indices)
        indices.sort()
        print("Sampled indices: ",indices)

        data = json.dumps({"indices":indices})
        s.send(data.encode())

        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        keys_selected = data.get("keys_selected")
        print("selected keys received from sender: ",keys_selected)


        print("----------------------------")

        with open("comm.data","rb") as f:
            Comm = pickle.load(f)
        
        # opening and verifying commitments
        # i = index of selected circuits
        # j = iterates through number of inputs in every circuit
        # count = to maintain count of selected garbled circuit to verify
        count = 0
        with open("cut-and-choose.json") as f:
            for i in range(0,len(indices)):
                TAGS = []
                for j in range(0,len(inputs)):
                    k_cube = pow(keys_selected[i][j],3,N)
                    k_cube_hash = hashlib.sha256(format(k_cube,'b')).hexdigest()
                    k_hash = hashlib.sha256(format(keys_selected[i][j], 'b')).hexdigest()

                    # print("Comm: {} , Key: {}, hash: {}".format(COMM[indices[i]],keys_selected[i],k_cube_hash))
                    print("-----------------------------------")
                    if k_cube_hash == Comm[indices[i]][j][inputs[j]][0]:
                        print("Commitment opened successfully!")
                    
                    # getting tags from commitments
                    tag_int = int(k_hash, 16)^Comm[indices[i]][j][inputs[j]][1]
                    print("-----------------------------------")
                    #tag_int = int(k_hash, 16)^COMM[indices[i]][j][1]
                    tag = gc_util.decode_str(tag_int)
                    TAGS.append(tag)
                
                print("count: {} indices[{}]={}".format(count,i,indices[i]))
                # load only circuits whose indices have been selected
                # TODO: POSSIBLE BUG here
                if count != indices[i]:
                        while count != indices[i]:
                            count += 1
                            line = f.readline()
                
                line = f.readline()
                data = json.loads(line)
                count += 1
                print("---------------------------------------")
                print("Input to circuit {} = {}".format(i,TAGS))
                mycirc = evaluator.Circuit(data)
                print(mycirc.fire(TAGS))
                print("---------------------------------------")

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

    server.bind(('',0))

    print("Proxy server started at ", server.getsockname())

    newthread = ClientThread()
    newthread.start()

