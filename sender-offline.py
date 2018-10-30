from __future__ import print_function

import socket
import threading
from util.commitment import Double_Commitment 
import random 
import hashlib 
import json 
import garbler_test  
import os 
import pickle
from util import *

#variables
MAX_DATA_RECV = 999999
# no of circuits
# TODO: Increase n to practical value
n = 5
# global list containing all witness keys and commitments
# for all N circuits generated
KEYS = []
A_All = []

# DEBUG
K_all = []
Comm_All = []

class ProxyThread(threading.Thread):

    def __init__(self, proxyaddr, proxysock):
        threading.Thread.__init__(self)
        self.proxy_socket = proxysock
        print("New proxy connection made at: ", proxyaddr)

    def run(self):
        
        # ---------- TO BE DONE JUST ONCE ----------
        
        # send CONN_COUNT to proxy then write to file for ckt eval step
        data = json.dumps({"CONN_COUNT":CONN_COUNT})
        self.proxy_socket.send(data.encode())

        # receive inputs from proxy - remaisn same throughout
        data = self.proxy_socket.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        inputs = data.get("inputs")
        print("received inputs: {} from proxy".format(inputs))
        
        # creation of RSA modulus n by Sender i.e n=p*q
        # TODO: check for bit size for RSA primes
        pub_key,priv_key = GM.GM_keygen(12)
        N = pub_key[1]
        p,q = priv_key[0],priv_key[1]
       
        while True:
            C = random.SystemRandom().randint(1,N-1)
            if util.gcd(C,N)==1:
                break

        data = json.dumps({"pub_key":pub_key, "C":C, "CONN_COUNT":CONN_COUNT})
        self.proxy_socket.send(data.encode())
        print("Sent public key {} , C {} , CONN_COUNT {} to proxy".format(pub_key,C,CONN_COUNT))
        key_gen = {"pub_key":pub_key, "priv_key":priv_key}
       
        
        # ---------- END ---------

        # ---------- TO BE DONE FOR EVERY CIRCUIT ----------
       
        global CIRCUITS

        for i in range(0,n):
            
            k = []
            A = []
            K = []
            Comm = []
            for j in range(0,mycirc.num_inputs):
                tags = []
                keys = []
                try:
                    t0 = CIRCUITS[i].poss_inputs[j][0]
                    t1 = CIRCUITS[i].poss_inputs[j][1]
                    print("Tag0: {} Tag1: {}".format(t0,t1))
                    tags.append(t0)
                    tags.append(t1)
                except:
                    raise ValueError("Something went wrong with tag generation!")

                print("---------------------------------")
                
                keys.append(random.SystemRandom().randint(1,N-1))
                keys.append(random.SystemRandom().randint(1,N-1))
                K.append(keys)
                
                a = random.SystemRandom().getrandbits(1)
                A.append(a)

                C0 = Double_Commitment(keys[a],tags[a],N).commitment
                C1 = Double_Commitment(keys[1-a],tags[1-a],N).commitment
                Comm.append([C0,C1])

                if inputs[j] == 0:
                    k.append(keys[a])
                else:
                    k.append(keys[1-a])
                print("-----------------------------------")
            
            global A_All, KEYS, K_all, Comm_All 
            A_All.append(A)
            KEYS.append(k)
            K_all.append(K)
            Comm_All.append(Comm)
       
        print("----------------------------")
        print("Keys all: ",K_all)
        print("Selected keys: [{},{}] [{},{}], [{},{}]".format(K_all[1][0][0],K_all[1][0][1],K_all[3][0][0],K_all[3][0][1],K_all[4][0][0],K_all[4][0][1]))
        print("----------------------------")
        # print("Selected comm: [{},{}],\n [{},{}], \n [{},{}]\n".format(Comm_All[1][0][0],Comm_All[1][0][1],Comm_All[3][0][0],Comm_All[3][0][1],Comm_All[4][0][0],Comm_All[4][0][1]))
        print("A values for all inputs*n: ",A_All)
        print("----------------------------")
        
        with open("key.data","wb") as f:
            pickle.dump(K_all, f)

        with open("comm.data", "wb") as f:
            pickle.dump(Comm_All, f)
        
        with open('comm.data','rb') as f:
            new_comm = pickle.load(f)

        print("----------------------------")
        
        """
        count_comm = 0
        for i in range(0,n):
            for j in range(0,len(inputs)):
                print("Comm:{} COMM: {}".format(new_comm[i][j][inputs[j]][0],COMM[i][j][0]))
                if COMM[i][j][0] == new_comm[i][j][inputs[j]][0]:
                    print("verified")
                    count_comm += 1
        print("Verified counts ( ideal- 20 ): ",count_comm)
        """
        # ----------- END ----------

        """        
        data = json.dumps({"COMM":COMM})
        self.proxy_socket.send(data.encode())
        """

        print("KEYS: ",KEYS)

        # receive indices of selected circuits
        data = self.proxy_socket.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        indices = data.get("indices")
        print("indices received: ",indices)

        keys_selected = []
        for i in indices:
            keys_selected.append(KEYS[i])

        data = json.dumps({"keys_selected":keys_selected})
        self.proxy_socket.send(data.encode())
        print("Sent seleted keys to proxy: ",keys_selected)

        with open("test/init.json","w") as f:
            data = {"pub_key":pub_key,"priv_key":priv_key,"CONN_COUNT":CONN_COUNT,"A":A_All,"indices":indices}
            json.dump(data,f)

if __name__ == "__main__":
   
    try:
        # creating socket and connecting to single proxy
        sender_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

        sender_server.bind(('',0))
        # allow sender server to spawn several threads when proxy connects with new client
        print("Sender server started at : ",sender_server.getsockname())
    except socket.error as e:
        print("An error occurred : ",e)


    try: 
        """
        try:
            CONN_COUNT = int(raw_input("Enter number of bidders: "))
        except ValueError:
            print("Please enter integer value")
            exit(0)

        on_input_gates = [[0, "AND", [0, 1]], 
                    [1, "XOR", [2, 3]], 
                    [2, "OR", [0,3]]]

        mid_gates = [[3, "XOR", [0, 1]],
                 [4, "OR", [1, 2]]]

        output_gates = [[5, "OR", [3, 4]]]
        """
        with open("test/circuit.json",'r') as f:
            data = json.load(f)
        data = json_util.byteify(data)

        CONN_COUNT = data.get("num_inputs")
        on_input_gates = data.get("on_input_gates")
        mid_gates = data.get("mid_gates")
        inter_gates = data.get("inter_gates")
        output_gates = data.get("output_gates")
        # remove old cut-and-choose.json, comm.json, keys.json
        if os.path.isfile("test/cut-and-choose.json"):
            os.remove("test/cut-and-choose.json")
    
        # list containing all circuit objects
        CIRCUITS = []

        for i in range(0,n):
            mycirc = garbler_test.Circuit(CONN_COUNT, on_input_gates, mid_gates, inter_gates, output_gates)
            # print("Circuit number: {} Possible inputs: {}".format(i+1,mycirc.poss_inputs))
            filename = "cut-and-choose.json"
            mycirc.prep_for_json_cut_n_choose(filename) 
            CIRCUITS.append(mycirc)

        # print("Circuit objects: ",CIRCUITS)
        with open("circuit.data","wb") as f:
            pickle.dump(CIRCUITS, f)
   
        sender_server.listen(1)
        proxysock, proxyaddr = sender_server.accept()
        newthread = ProxyThread(proxyaddr,proxysock)
        newthread.start()

    except KeyboardInterrupt:
        print("Shutting down...")
        exit(0)


