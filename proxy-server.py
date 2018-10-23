from __future__ import print_function

import socket
import os
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
# stores all chosen tags received from sender
TAGS = []

# create lock to keep track of number
# of connections whenever new bidder joins
lock = threading.Lock()
CONN_COUNT = 0

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
            global count,TAGS
            count = data.get("count")
            TAGS = [None]*count 

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
        C0,C1,CO = data.get("C0"),data.get("C1"),data.get("CO")
        N = pub_key[1]
        print("Received pub_key: {}, C: {}, C0: {}, C1: {}, CO:{} from sender".format(pub_key,C,C0,C1,CO))
        print("-------------------------------------")

        # 3. Chooser receives pub_key,C from proxy
        data = json.dumps({"pub_key":pub_key, "C":C})
        print("Sent pub_key: {},C: {} to chooser from proxy".format(pub_key,C))
        self.client_socket.send(data.encode())
        print("-------------------------------------")
        
        # 4. Chooser sends (x0,v,x) to proxy. Proxy sends (x0,v) to sender
        data = self.client_socket.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        x0,v,x,bp = data.get("x0"),data.get("v"),data.get("x"),data.get("bp")
        print("Received x0: {}, v: {}, x:{}, bp:{} from sender".format(x0,v,x,bp))

        # send (x0,v) to sender
        data = json.dumps({"x0":x0, "v":v})
        s.send(data.encode())
        print("Sent x0:{}, v: {} to sender".format(x0,v))


        # 5. Proxy receives (z0,z1),u from sender
        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        z0,z1,u = data.get("z0"),data.get("z1"),data.get("u")
        print("Received z0:{}, z1:{}, u:{} from sender".format(z0,z1,u))

        
        # 7. Proxy computes z0^3 and z1^3 and checks H(z0^3/x0) and
        # H(z1^3/x1) are equal to 1st element of C0, C1
        x1 = (C*x0)%N
        z_a = util.modular_div_util(pow(z0,3),x0,N)
        z_b = util.modular_div_util(pow(z1,3),x1,N)
        hash_z0 = hashlib.sha256(format(z_a,'b')).hexdigest()
        hash_z1 = hashlib.sha256(format(z_b,'b')).hexdigest()
        # print("H(z0^3/x0):  ",hash_z0,"\n H(z1^3/x1):  ",hash_z1)
        
        # verifying that sender sent correct tags he had committed to - VERIFIABLE PROXY
        
        print("-------------------------------------")
        if ( hash_z0 == C0[0] or hash_z0 == C1[0] ) and ( hash_z1 == C0[0] or hash_z1 == C1[0] ):
            print("Verified sender tags")
        else:
            print("The sender isn't sending the right tags")
        print("-------------------------------------")

        # FINAL : Verify c published by sender
        # TODO: Verify c publshed by sender
        # 7. Proxy verifies that he can use x to open C0 if c=0
        # else use x to open C1 if c=1
        data = s.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        c = int(data.get("c"))

        if bp==0:
            k = util.modular_div_util(z0,x,N)
        else:
            # print("Changed c")
            # TODO: Important: Figure why c doesn't work when bp==1
            k = util.modular_div_util(z1,x,N)
            c = 1-c

        
        k_hash = hashlib.sha256(format(k,'b')).hexdigest()
        
        # DEBUG:
        #print("k: {} --------- k_hash: {}".format(k,k_hash))
        # print("bp: ",bp," Type bp = ",type(bp))
        
        k_cube = pow(k,3,N)
        k_cube_hash = hashlib.sha256(format(k_cube,'b')).hexdigest()
        if k_cube_hash == C0[0]:
            print("Opened C0")
        elif k_cube_hash == C1[0]:
            print("Opened C1")

        if c==0:
            tag_int = int(k_hash,16)^C0[1]
        else:
            tag_int = int(k_hash, 16)^C1[1]
    
        print("c: {}, k:{} ".format(c,k))
        print("tag_int: ",tag_int) 
        
        print("-------------------------------------")
        
        data = json.dumps({"tag_int":tag_int})
        self.client_socket.send(data.encode())
        print("Sent tag_int: {} to bidder".format(tag_int))

        print("-------------------------------------")

        tag = gc_util.decode_str(tag_int)
        lock.acquire()
        TAGS[CONN_COUNT-1] = tag 
        print("TAGS[{}] = {}".format(CONN_COUNT-1,TAGS[CONN_COUNT-1]))
        lock.release()
        print("TAGS: ",TAGS)
        print("-------------------------------------")
        
        # ------ EVALUATION ------
        if count == CONN_COUNT:
            print("Inputs to circuit: {}".format(TAGS))
            print(mycirc.fire(TAGS))
            server.close()
            print("Shutting down...")
            os._exit(0)

        print("Server at {} disconnected".format(clientaddr))
        print("-------------------------------------")
        s.close()

# ------- EVALUATOR -------- 
if __name__ == "__main__":
    
    with open('test/garbled_circuit.json') as data_file:
        data = json.load(data_file)
    
    mycirc = evaluator.Circuit(data)

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

