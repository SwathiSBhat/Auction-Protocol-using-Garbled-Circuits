from __future__ import print_function

import socket
import os
import json 
import thread
import threading 
import hashlib
from util import *
import evaluator_test 
import yappi 
from datetime import datetime 
import sys 

# variables
BACKLOG = 50
MAX_DATA_RECV = 4096
count = 0
# stores all chosen tags received from sender
TAGS = []

# create lock to keep track of number
# of connections whenever new bidder joins
lock = threading.Lock()
CONN_COUNT = 0
ip_len = 0

# config of sender-server
SERVER = '127.0.0.1'
PORT = int(raw_input("Enter sender-server port number: "))

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
        # TODO - Catch conn reset error
        s.connect((SERVER,PORT))
        # 0. Receive number of bidders in the system
        # Send conn_count to sender so that sender can initialize tags
        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        if CONN_COUNT == 1:
            global count,TAGS,ip_len
            count = data.get("count")
            ip_len = data.get("ip_len")
            TAGS = [None]*count*ip_len 

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
        N = pub_key[1]
        print("Received pub_key: {}, C: {}, Comm:{} CO:{} from sender".format(pub_key,C,comm,CO))
        print("-------------------------------------")

        # 3. Chooser receives pub_key,C from proxy
        data = json.dumps({"pub_key":pub_key, "C":C})
        print("Sent pub_key: {},C: {} to chooser from proxy".format(pub_key,C))
        self.client_socket.send(data.encode())
        print("-------------------------------------")
        
        # 4. Chooser sends (x0,v,x) to proxy. Proxy sends (x0,v) to sender
        data = self.client_socket.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        x0,v,x,bid_p = data.get("x0"),data.get("v"),data.get("x"),data.get("bp")
        print("Received x0: {}, v: {}, x:{}, bp:{} from sender".format(x0,v,x,bid_p))

        # send (x0,v) to sender
        data = json.dumps({"x0":x0, "v":v})
        s.send(data.encode())
        print("Sent x0:{}, v: {} to sender".format(x0,v))


        # 5. Proxy receives (z0,z1),u from sender
        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        z0,z1,u,c = data.get("z0"),data.get("z1"),data.get("u"),data.get("c")
        print("Received z0:{}, z1:{}, u:{}, c:{} from sender".format(z0,z1,u,c))

        
        # 7. Proxy computes z0^3 and z1^3 and checks H(z0^3/x0) and
        # H(z1^3/x1) are equal to 1st element of C0, C1
        TAG_INT = []

        for i in range(ip_len):
            x1 = (C[i]*x0[i])%N
            z_a = util.modular_div_util(pow(z0[i],3),x0[i],N)
            z_b = util.modular_div_util(pow(z1[i],3),x1,N)
            hash_z0 = hashlib.sha256(format(z_a,'b')).hexdigest()
            hash_z1 = hashlib.sha256(format(z_b,'b')).hexdigest()
            # print("H(z0^3/x0):  ",hash_z0,"\n H(z1^3/x1):  ",hash_z1)
        
            # verifying that sender sent correct tags he had committed to - VERIFIABLE PROXY
        
            print("-------------------------------------")
            print("hash_z0 = {} hash_z1 = {} comm[i][1][0] : {} comm[i][0][0]:{}".format(hash_z0,hash_z1,comm[i][1][0],comm[i][0][0]))
            if ( hash_z0 == comm[i][0][0] or hash_z0 == comm[i][1][0] ) and ( hash_z1 == comm[i][0][0] or hash_z1 == comm[i][1][0] ):
                print("Verified sender tags")
            else:
                print("The sender isn't sending the right tags")
                print("Aborting...")
                os._exit(0)
            print("-------------------------------------")

            # FINAL : Verify c published by sender
            # TODO: Verify c publshed by sender
            # 7. Proxy verifies that he can use x to open C0 if c=0
            # else use x to open C1 if c=1
            """
            data = s.recv(MAX_DATA_RECV)
            data = json.loads(data.decode())
            c = int(data.get("c"))
            """
            if bid_p[i]==0:
                k = util.modular_div_util(z0[i],x[i],N)
            else:
            # print("Changed c")
            # TODO: Important: Figure why c doesn't work when bp==1
                k = util.modular_div_util(z1[i],x[i],N)
                c[i] = 1-int(c[i])

        
            k_hash = hashlib.sha256(format(k,'b')).hexdigest()
        
            # DEBUG:
            #print("k: {} --------- k_hash: {}".format(k,k_hash))
            # print("bp: ",bp," Type bp = ",type(bp))
        
            k_cube = pow(k,3,N)
            k_cube_hash = hashlib.sha256(format(k_cube,'b')).hexdigest()
            print("-------------------------------------")
            
            # TODO: BUG: without storing comm_val
            # comm[i][0][1] gives different values in next if and the one after that
            
            if k_cube_hash == comm[i][0][0]:
                comm_val = comm[i][0][1]
                print("Opened C0")
                # print("COMM: {} - {}".format(comm[i][0][0],comm[i][0][1]))
            elif k_cube_hash == comm[i][1][0]:
                comm_val = comm[i][1][1]
                print("Opened C1")
                # print("COMM: {} - {}".format(comm[i][1][0],comm[i][1][1]))
            
            if c[i]==0:
                #print("c:{} k_hash:{} k_hash {}-----comm {} ".format(c,k_hash,int(k_hash,16),comm[i][0][1]))
                #print("COMM: ",comm[i][0][1])
                tag_int = int(k_hash,16)^comm_val 
            else:
                #print("c:{} k_hash:{} k_hash {}-----comm {} ".format(c,k_hash,int(k_hash,16),comm[i][1][1]))
                #print("COMM: ",comm[i][1][1])
                tag_int = int(k_hash, 16)^comm_val 
            
            TAG_INT.append(tag_int)
            # DEBUG
            #print("c[i]: {}, k:{} ".format(c[i],k))
            #print("k:{} -------------- k_hash: {}".format(k,k_hash))
            #print("comm: ",k_cube_hash)
            #print("tag_int: ",tag_int) 
            print("-------------------------------------")
            
            tag = gc_util.decode_str(tag_int)
            lock.acquire()
            last_index = (ip_len*CONN_COUNT)-1
            TAGS[last_index-ip_len+i+1] = tag 
            #print("TAGS[{}] = {}".format(CONN_COUNT-1,TAGS[CONN_COUNT-1]))
            #print("Added tags: i:{} count:{}".format(i,CONN_COUNT))
            lock.release()
            #print("TAGS: ",TAGS)
            
            # ------ EVALUATION ------
            if i==ip_len-1 and CONN_COUNT == count:
                #print("Inside evaluation i: {} count: {}".format(i,CONN_COUNT))
                #print("Inputs to circuit: {}".format(TAGS))
                yappi.start()
                print(mycirc.fire(TAGS))
                func_stats = yappi.get_func_stats().print_all()
                # func_stats.save('callgrind.out.' + datetime.now().isoformat(), 'CALLGRIND')
                yappi.stop()
                yappi.clear_stats()
                data = json.dumps({"tag_int":TAG_INT})
                self.client_socket.send(data.encode())
                print("Sent tag_int: {} to bidder".format(TAG_INT))
                server.close()
                print("Shutting down...")
                os._exit(0)


            print("-------------------------------------")
        
        data = json.dumps({"tag_int":TAG_INT})
        self.client_socket.send(data.encode())
        print("Sent tag_int: {} to bidder".format(TAG_INT))

        print("-------------------------------------")
        
        """
        # ------ EVALUATION ------
        if count == CONN_COUNT:
            print("Inputs to circuit: {}".format(TAGS))
            print(mycirc.fire(TAGS))
            server.close()
            print("Shutting down...")
            os._exit(0)
        """
        print("Server at {} disconnected".format(clientaddr))
        print("-------------------------------------")
        s.close()

# ------- EVALUATOR -------- 
if __name__ == "__main__":
    
    with open('test/garbled_circuit.json') as data_file:
        data = json.load(data_file)
    
    mycirc = evaluator_test.Circuit(data)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

    server.bind(('',0))

    print("Proxy server started at ", server.getsockname())

    while True:
        try:
            server.listen(BACKLOG)
            clientsock, clientaddr = server.accept()
            newthread = ClientThread(clientaddr, clientsock)
            newthread.start()
        except KeyboardInterrupt:
            print("Shutting down.....")
            exit(0)

