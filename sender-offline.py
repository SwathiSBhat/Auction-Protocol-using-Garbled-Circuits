#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : sender-offline.py
# Author            : Swathi S Bhat
# Date              : 09.12.2018
# Last Modified Date: 13.12.2018
# Last Modified By  : Swathi S Bhat
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
from halo import Halo 
from termcolor import colored
import subprocess
import yappi 
import sys 

#variables
MAX_DATA_RECV = 999999
IS_NOT_GATE = 0
# no of circuits
# TODO: Increase n to practical value
n = 10 
# global list containing all witness keys and commitments
# for all N circuits generated
KEYS = []
A_All = []

# DEBUG
K_all = []
Comm_All = []
not_tag = []

pub_key, priv_key = 0, 0
C = 0

def print_stat(stats, out, limit=None):
    if stats.empty():
        return 
    sizes = [36, 5, 8, 8, 8]
    columns = dict(zip(range(len(yappi.COLUMNS_FUNCSTATS)), 
                         zip(yappi.COLUMNS_FUNCSTATS, sizes)))
    
    print(yappi.COLUMNS_FUNCSTATS)
    
    show_stats = stats
    if limit:
        show_stats = stats[:limit]
    out.write(os.linesep)
    for stat in show_stats:
        stat._print(out, columns)


def compute():
    

    # creation of RSA modulus n by Sender i.e n=p*q
    global pub_key, priv_key , C
    pub_key,priv_key = GM.GM_keygen(128)
    N = pub_key[1]
    p,q = priv_key[0],priv_key[1]
       
    while True:
        C = random.SystemRandom().randint(1,N-1)
        if util.gcd(C,N)==1:
            break

    with open('json/inputs.json','r') as f:
        data = json.load(f)
    inputs = data["inputs"]
    # print("received inputs: {} from proxy".format(inputs))
    
    global CIRCUITS

    # to make sure commitments for NOT gate input is not made
    num_inputs = mycirc.num_inputs 
        
    if IS_NOT_GATE:
        num_inputs = mycirc.num_inputs - 1
        for i in range(0, n):
            not_tag.append(CIRCUITS[i].poss_inputs[num_inputs][1])
            # if i > 95:
            #    print("circuit: {} not_tag: {}".format(i,not_tag[i]))

    for i in range(0,n):
            
        k = []; A = []; K = []; Comm = []

        for j in range(0,num_inputs):
            tags = []
            keys = []
            try:
                t0 = CIRCUITS[i].poss_inputs[j][0]
                t1 = CIRCUITS[i].poss_inputs[j][1]
                #if i<10:
                #   print("------------------------------------")
                #    print("i:{} Tag0: {} Tag1: {}".format(i,t0,t1))
                #    print("------------------------------------")
                tags.append(t0)
                tags.append(t1)
            except:
                print("Something went wrong with tag generation!")
                print("Aborting...")
                os._exit(0)    

            keys.append(random.SystemRandom().randint(1,N-1))
            keys.append(random.SystemRandom().randint(1,N-1))
            K.append(keys)
                
            a = random.SystemRandom().getrandbits(1)
            A.append(a)

            C0 = Double_Commitment(keys[a],tags[a],N).commitment
            C1 = Double_Commitment(keys[1-a],tags[1-a],N).commitment
            Comm.append([C0,C1])

            k.append(keys[inputs[j]])
            
        global A_All, KEYS, K_all, Comm_All 
        A_All.append(A)
        KEYS.append(k)
        K_all.append(K)
        Comm_All.append(Comm)
       
    with open("data/key.data","wb") as f:
        pickle.dump(K_all, f)

    with open("data/comm.data", "wb") as f:
        pickle.dump(Comm_All, f)

    if IS_NOT_GATE:
        with open("data/not_tag.data","wb") as f:
            pickle.dump(not_tag, f)

    with open('json/indices.json','r') as f:
        data = json.load(f)
    indices = data["indices"]
    # print("indices received: ",indices)

    keys_selected = []
    for i in indices:
        keys_selected.append(KEYS[i])

    # data = json.dumps({"keys_selected":keys_selected})
    data = {"keys_selected":keys_selected}
    with open('json/keys_selected.json','w') as f:
        json.dump(data, f)
    # self.proxy_socket.send(data.encode())
    # print("Sent seleted keys to proxy: ",keys_selected)
    print(colored("Sent {} keys to proxy for verification: ".format(len(keys_selected)),"yellow"))

    with open("test/init.json","w") as f:
        data = {"pub_key":pub_key,"priv_key":priv_key,"CONN_COUNT":CONN_COUNT,"A":A_All,"indices":indices}
        json.dump(data,f)


class ProxyThread(threading.Thread):

    def __init__(self, proxyaddr, proxysock):
        threading.Thread.__init__(self)
        self.proxy_socket = proxysock
        print("New proxy connection made at: ", proxyaddr)

    def run(self):

        data = json.dumps({"pub_key":pub_key, "C":C, "CONN_COUNT":CONN_COUNT})
        self.proxy_socket.send(data.encode())
        print("Sent public key {} , C {} , CONN_COUNT {} to proxy".format(pub_key,C,CONN_COUNT))
        

if __name__ == "__main__":

    try: 
        with open("test/circuit.json",'r') as f:
            data = json.load(f)
        data = json_util.byteify(data)

        CONN_COUNT = data.get("num_inputs")
        on_input_gates = data.get("on_input_gates")
        mid_gates = data.get("mid_gates")
        inter_gates = data.get("inter_gates")
        output_gates = data.get("output_gates")
        ip_len = data.get("ip_len")

        """
        on_input_gates = [[0, "AND", [0, 1]], 
                    [1, "XOR", [2, 3]], 
                    [2, "OR", [0,3]]]

        mid_gates = [[3, "XOR", [0, 1]],
                 [4, "OR", [1, 2]]]
        
        output_gates = [[5, "OR", [3, 4]],[6, "AND", [1, 4]]]
        """

        num_inputs = CONN_COUNT
        # checking for presence of NOT gate as input gate
        for i in range(0, len(on_input_gates)):
            if on_input_gates[i][1] == "NOT":
                IS_NOT_GATE = 1
                break

        if IS_NOT_GATE:
            num_inputs += 1

        # remove old cut-and-choose.json, comm.json, keys.json
        if os.path.isfile("test/cut-and-choose.json"):
            os.remove("test/cut-and-choose.json")

        # remove old not_tag data
        if os.path.isfile("data/not_tag.data"):
            os.remove("data/not_tag.data")
    
        # list containing all circuit objects
        CIRCUITS = []

        spinner = Halo(text="Generating garbled circuits", spinner='dots', text_color="green")
        
        # calculating time for execution
        # yappi.start()

        spinner.start()
        for i in range(0,n):
            mycirc = garbler_test.Circuit(num_inputs, on_input_gates, mid_gates, inter_gates, output_gates)
            filename = "cut-and-choose.json"
            mycirc.prep_for_json_cut_n_choose(filename, IS_NOT_GATE, ip_len) 
            CIRCUITS.append(mycirc)
        print("\n")
        spinner.succeed('Successfully generated garbled circuits')
        spinner.stop()

        # func_stats = yappi.get_func_stats()
        # print_stat(func_stats, sys.stdout, limit=10)
        # func_stats = yappi.get_func_stats().print_all()
        # yappi.stop()
        # yappi.clear_stats()

        # calling proxy_gen_indices.py to generate indices and inputs
        subprocess.call(['python', "circuit/proxy_gen_indices.py", str(CONN_COUNT), str(n)])

        # print("Circuit objects: ",CIRCUITS)
        with open("data/circuit.data","wb") as f:
            pickle.dump(CIRCUITS, f)

        compute()

        try:
            # creating socket and connecting to single proxy
            sender_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sender_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

            sender_server.bind(('',0))
            # allow sender server to spawn several threads when proxy connects with new client
            print(colored("Sender server started at : ","white"),sender_server.getsockname())
        except socket.error as e:
            print("An error occurred : ",e)
        
        print(colored("Connect to proxy now...","white"))

        sender_server.listen(1)
        proxysock, proxyaddr = sender_server.accept()
        newthread = ProxyThread(proxyaddr,proxysock)
        newthread.start()

    except KeyboardInterrupt:
        spinner = Halo(text="Keyboard Interrupt. Shutting down", spinner='dots')
        spinner.start()
        # print("Shutting down...")
        spinner.fail()
        exit(0)


