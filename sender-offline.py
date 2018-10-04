from __future__ import print_function

import socket
import threading
import GM  
from commitment import Double_Commitment 
import random 
import hashlib 
import json 
import util
import cuberoot 
import garbler  

#variables
MAX_DATA_RECV = 999999
# no of circuits
# TODO: Increase n to practical value
n = 5
# global list containing all witness keys and commitments
# for all N circuits generated
KEYS = []
COMM = []

class ProxyThread(threading.Thread):

    def __init__(self, proxyaddr, proxysock):
        threading.Thread.__init__(self)
        self.proxy_socket = proxysock
        print("New proxy connection made at: ", proxyaddr)

    def run(self):
        
        # ---------- TO BE DONE JUST ONCE ----------
        
        # receive inputs from proxy - remaisn same throughout
        data = self.proxy_socket.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        inputs = data.get("inputs")
        print("received inputs: {} from proxy".format(inputs))
        
        # creation of RSA modulus n by Sender i.e n=p*q
        # TODO: check for bit size for RSA primes
        # TODO: check if this n is the same as that used in GM
        pub_key,priv_key = GM.GM_keygen(12)
        N = pub_key[1]
        p,q = priv_key[0],priv_key[1]
       
        while True:
            C = random.SystemRandom().randint(1,N-1)
            if util.gcd(C,N)==1:
                break

        data = json.dumps({"pub_key":pub_key, "C":C})
        self.proxy_socket.send(data.encode())
        print("Sent public key {} , C {} to proxy".format(pub_key,C))
        
        # ---------- END ---------

        # ---------- TO BE DONE FOR EVERY CIRCUIT ----------
        
        # TODO: Change range to number of circuits (N) to be created
        for i in range(0,4):
            tags = []
            try:
                t0 = mycirc.poss_inputs[i][0]
                t1 = mycirc.poss_inputs[i][1]
                print("Tag0: {} Tag1: {}".format(t0,t1))
                tags.append(t0)
                tags.append(t1)
            except:
                raise ValueError("Something went wrong with tag generation!")

            print("---------------------------------")
        
            k0 = random.SystemRandom().randint(1,N-1)
            k1 = random.SystemRandom().randint(1,N-1)
            # DEBUG
            # print("k0: {} k1: {}".format(k[0],k[1]))
        
            C0 = Double_Commitment(k0,tags[0],N).commitment
            C1 = Double_Commitment(k1,tags[1],N).commitment
            global KEYS,COMM
            if inputs[i] == 0:
                COMM.append(C0)
                KEYS.append(k0)
                print("Input: {} Comm: {} Key: {} Comm[0]: {} ".format(inputs[i],C0,k0,C0[0]))
            else:
                COMM.append(C1)
                KEYS.append(k1)
                print("Input: {} Comm: {} Key: {} Comm[0]: {} ".format(inputs[i],C1,k1,C1[0]))



        # ----------- END ----------

        # send all commitments at once
        # TODO: Check if data recv size is sufficient if 
        # all commitments are sent at once
        data = json.dumps({"COMM":COMM})
        self.proxy_socket.send(data.encode())

        # DEBUG
        print("COMM: ",COMM)
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


# creating socket and connecting to single proxy
sender_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

sender_server.bind(('',0))

# allow sender server to spawn several threads when proxy connects with new client
print("Sender server started at : ",sender_server.getsockname())


if __name__ == "__main__":
    
    on_input_gates = [[0, "AND", [0, 1]], 
                    [1, "XOR", [2, 3]], 
                    [2, "OR", [0,3]]]

    mid_gates = [[3, "XOR", [0, 1]],
                 [4, "OR", [1, 2]]]

    output_gates = [[5, "OR", [3, 4]]]

    with open("cut-and-choose.json","a") as f:
        for i in range(0,n):
            mycirc = garbler.Circuit(4, on_input_gates, mid_gates, output_gates)
            print("Circuit number: {} Possible inputs: {}".format(i+1,mycirc.poss_inputs))
            

    sender_server.listen(1)
    proxysock, proxyaddr = sender_server.accept()
    newthread = ProxyThread(proxyaddr,proxysock)
    newthread.start()


