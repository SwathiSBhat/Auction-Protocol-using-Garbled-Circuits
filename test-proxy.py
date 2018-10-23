from __future__ import print_function

import socket
import os
import sys
import json 
import thread
import threading 
import hashlib
from util import *
import evaluator

# variables
BACKLOG = 50
MAX_DATA_RECV = 999999
count = 0

# n = number circuits to be evaluated = N/2 
# where N = total number of circuits
n = 3

# stores all chosen tags received from sender
TAGS = []
TAGS_ALL = []

# create lock to keep track of number
# of connections whenever new bidder joins
lock = threading.Lock()
CONN_COUNT = 0

# print("CONN_COUNT: ",CONN_COUNT)
# TODO: Take number of bidders as input here and refuse connections if 
# bidders exceed connection count

# config of sender-server
SERVER = '127.0.0.1'
# PORT = int(raw_input("Enter sender-server port number: "))
PORT = 50000

class ClientThread(threading.Thread):

    def __init__(self, clientaddr, clientsocket):
        threading.Thread.__init__(self)
        self.client_socket = clientsocket
        
        # blocks incrementing count for other threads
        global CONN_COUNT
        lock.acquire()
        CONN_COUNT += 1
        lock.release()

        print("Connection number: ",CONN_COUNT,"  made at: ",clientaddr)
        print("-------------------------------------")

    def run(self):
        # create a socket to connect to sender/server from proxy
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER,PORT))
        # 0. Receive number of bidders in the system
        # Send conn_count to sender so that sender can initialize tags
        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        if CONN_COUNT == 1:
            global count,TAGS,TAGS_ALL
            count = data.get("count")
            print("number of bidders: ",count)
            TAGS = [[None for x in range(count)] for y in range(n)]
            print("Iniialized TAGS to: ",TAGS)

        """
        VPOT Protocol
        """

        data = json.dumps({"conn_count":CONN_COUNT})
        s.send(data.encode())
        print("Sent CONN_COUNT: {} to sender".format(CONN_COUNT))
        print("-------------------------------------")

        # 2. Sender sends pub_key,C, (C0,C1) and CO to proxy
        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        pub_key,C = data.get("pub_key"),data.get("C")
        comm,CO = data.get("comm"),data.get("CO")
        indices_eval = data.get("indices")
        N = pub_key[1]
        print("Received pub_key: {}, C: {},  CO:{} indices:{} from sender".format(pub_key,C,CO,indices_eval))
        print("-------------------------------------")

        # 3. Chooser receives pub_key,C from proxy
        data = json.dumps({"pub_key":pub_key, "C":C})
        print("Sent pub_key: {},C: {} to chooser from proxy".format(pub_key,C))
        self.client_socket.send(data.encode())
        print("-------------------------------------")
        
        # 4. Chooser sends (x0,v,x) to proxy. Proxy sends (x0,v) to sender
        data = self.client_socket.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        X0,v,X,bp = data.get("x0"),data.get("v"),data.get("x"),data.get("bp")
        print("Received x0: {}, v: {}, x:{}, bp:{} from sender".format(X0,v,X,bp))

        # send (x0,v) to sender
        data = json.dumps({"x0":X0, "v":v})
        s.send(data.encode())
        print("Sent x0:{}, v: {} to sender".format(X0,v))


        # 5. Proxy receives (z0,z1),u from sender
        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        Z,u,c = data.get("Z"),data.get("u"),data.get("c")
        print("Received Z:{}, u:{}, c:{} from sender".format(Z,u,c))


        # 7. Proxy computes z0^3 and z1^3 and checks H(z0^3/x0) and
        # H(z1^3/x1) are equal to 1st element of C0, C1
        for i in range(0,len(indices_eval)):
            x1 = (C[i]*X0[i])%N
            z_a = util.modular_div_util(pow(Z[i][0],3),X0[i],N)
            z_b = util.modular_div_util(pow(Z[i][1],3),x1,N)
            hash_z0 = hashlib.sha256(format(z_a,'b')).hexdigest()
            hash_z1 = hashlib.sha256(format(z_b,'b')).hexdigest()
            # print("H(z0^3/x0):  ",hash_z0,"\n H(z1^3/x1):  ",hash_z1)
            
            print("-------------------------------------")
            if ( hash_z0 == C0[0] or hash_z0 == C1[0] ) and ( hash_z1 == C0[0] ) or ( hash_z1 == C1[0] ):
                print("Verified sender tags")
            else:
                print("The sender isn't sending the right tags")
            print("-------------------------------------")

            # FINAL : Verify c published by sender
            # TODO: Verify c publshed by sender
            # 7. Proxy verifies that he can use x to open C0 if c=0
            # else use x to open C1 if c=1
                
            print("bp: {} type(bp): {}".format(bp,type(bp)))
            if bp==0:
                k = util.modular_div_util(Z[i][0],X[i],N)
            else:
                # print("Changed c")
                # TODO: Important: Figure why c doesn't work when bp==1
                k = util.modular_div_util(Z[i][1],X[i],N)
                c[i] = 1-int(c[i])

              
            k_hash = hashlib.sha256(format(k,'b')).hexdigest()
        
            # DEBUG:
            print("k: {} --------- k_hash: {}".format(k,k_hash))
            # print("bp: ",bp," Type bp = ",type(bp))
        
            k_cube = pow(k,3,N)
            k_cube_hash = hashlib.sha256(format(k_cube,'b')).hexdigest()
            if k_cube_hash == comm[i][0][0]:
                print("Opened C0, k_cube_hash: ",k_cube_hash)
            elif k_cube_hash == comm[i][1][0]:
                print("Opened C1, k_cube_hash: ",k_cube_hash)

            if int(c[i]) == 0:
                tag_int = int(k_hash,16)^comm[i][0][1]
            else:
                tag_int = int(k_hash, 16)^comm[i][1][1]
    
            print("c: {}, k:{} ".format(c[i],k))
            print("tag_int: ",tag_int) 

            print("-------------------------------------")
        
            tag = gc_util.decode_str(tag_int)
            lock.acquire()
            print("i: {} CONN_COUNT-1: {}".format(i,CONN_COUNT-1))
            TAGS[i][CONN_COUNT-1] = tag 
            print("TAGS[{}][{}] = {}".format(i,CONN_COUNT-1,TAGS[i][CONN_COUNT-1]))
            lock.release()
            # print("TAGS: ",TAGS)
            print("-------------------------------------")
    
            # print("Inputs to circuit number {}: {}".format(indices[i],TAGS))
        
        print("Bidder{} inputs to all circuits: {}".format(CONN_COUNT,TAGS))
        
        print("-------------------------------------")
        
        """
        if CONN_COUNT == count:        
            print("All inputs: ",TAGS)
            lock.acquire()
            TAGS_ALL.append(TAGS)
            lock.release()
        """

        # TODO: Don't send entire TAGS just send corresponding ones
        data = json.dumps({"tag_all":TAGS})    
        self.client_socket.send(data.encode())
        print("Sent tags for all ckts to bidder: {}".format(TAGS))

        # ------- EVALUATOR -------- 
        if count == CONN_COUNT:
            # cktcount = to keep circuit count to evaluate
            cktcount = 0
            with open("test/cut-and-choose.json") as f:
                for i in range(0,len(indices_eval)):
                    if cktcount != indices_eval[i]:
                        while cktcount != indices_eval[i]:
                            cktcount += 1
                            line = f.readline()
                    print("cktcount {} cktnumber: {}".format(cktcount,indices_eval[i]))
                    line = f.readline()
                    data = json.loads(line)
                    cktcount += 1
                    mycirc = evaluator.Circuit(data)
                    print(mycirc.fire(TAGS[i]))
                    print("-------------------------------------")
        
        
        # server.close()
        print("Server at {} disconnected".format(clientaddr))
        print("-------------------------------------")
        s.close()

        # TODO : If proxy quits, quit client and sender 
        # TODO : Figure out where to close client socket


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

server.bind(('127.0.0.1',50001))

print("Proxy server started at ", server.getsockname())

while True:
    server.listen(BACKLOG)
    clientsock, clientaddr = server.accept()
    newthread = ClientThread(clientaddr, clientsock)
    newthread.start()

