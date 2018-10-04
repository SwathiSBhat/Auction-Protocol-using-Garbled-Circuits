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

# variables
BACKLOG = 50
MAX_DATA_RECV = 999999

# config of sender-server
SERVER = '127.0.0.1'
PORT = int(raw_input("Enter sender-server port number: "))

class ClientThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        # create a socket to connect to sender/server from proxy
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER,PORT))

        # --------- TO BE DONE ONCE ---------
        
        # send inputs for which commitments are needed
        # TODO: Dynamically generate input
        inputs = [0,1,0,1]
        data = json.dumps({"inputs":inputs})
        s.send(data.encode())
        
        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        pub_key,C = data.get("pub_key"),data.get("C")
        print("Received pub_key {} and C {} from sender".format(pub_key,C))
        N = pub_key[1]

        # --------- END ------------

        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        COMM = data.get("COMM")
        print("Commitments received: ",COMM)

        # TODO: change sampling range to number of circuits
        num_of_indices = 2
        indices = random.SystemRandom().sample(range(0,4), num_of_indices)
        print("Sampled indices: ",indices)

        data = json.dumps({"indices":indices})
        s.send(data.encode())

        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        keys_selected = data.get("keys_selected")
        print("selected keys received from sender: ",keys_selected)

        # opening and verifying commitments
        for i in range(0,len(indices)):
            k_cube = pow(keys_selected[i],3,N)
            k_cube_hash = hashlib.sha256(format(k_cube,'b')).hexdigest()
           
            print("Comm: {} , Key: {}, hash: {}".format(COMM[indices[i]],keys_selected[i],k_cube_hash))

            if k_cube_hash == COMM[indices[i]][0]:
                print("Commitment opened successfully!")



with open('garbled_circuit.json') as data_file:
    data = json.load(data_file)

mycirc = evaluator.Circuit(data)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

server.bind(('',0))

print("Proxy server started at ", server.getsockname())

newthread = ClientThread()
newthread.start()

