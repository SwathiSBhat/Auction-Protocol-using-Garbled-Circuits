#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : auction_circuit.py
# Author            : Swathi S Bhat
# Date              : 07.12.2018
# Last Modified Date: 07.12.2018
# Last Modified By  : Swathi S Bhat
from __future__ import print_function

import os 
import json 

def input_gate(index1, index2, ip_gates, n, gate_num):
    ip_gates.append([gate_num, 'AND', [index1, index2]])
    ip_gates.append([gate_num + 1, 'NOT', [index1, n]])
    ip_gates.append([gate_num + 2, 'NOT', [index2, n]])
    ip_gates.append([gate_num + 3, 'NOT', [index2+1, n]])

def inter_gate(index1, index2, inter_gates, gate_num):
    inter_gates.append([gate_num + 4, 'AND', [index1, gate_num + 2], [True, False]])
    inter_gates.append([gate_num + 5, 'AND', [index1 + 1, gate_num + 3], [True, False]])

def mid_gate(mid_gates, gate_num):
    mid_gates.append([gate_num + 6, 'AND', [gate_num+1, gate_num+2]])
    mid_gates.append([gate_num + 7, 'OR', [gate_num, gate_num+6]])
    mid_gates.append([gate_num + 8, 'AND', [gate_num + 5, gate_num + 7]])

def output_gate(output_gates, gate_num):
    output_gates.append([gate_num + 9, 'OR', [gate_num + 4, gate_num + 8]])

if __name__ == "__main__":
    num_bidders = int(raw_input("Enter number of bidders: "))
    ip_len = int(raw_input("Enter length of bid: "))
    # n = index of input to NOT gate i.e last index
    n = num_bidders*ip_len
    if ip_len != 2:
        print("The circuit is tailored for 2 bit length bids. Exiting...")
        os._exit(0)
    # list a - stores starting bit index for every bidder
    # example - bidders X,Y,Z,W => a = [0, 2, 4, 6]
    # X has bits 01 , Y 23, Z 45, W 67
    a = [i for i in range(0,num_bidders*ip_len,ip_len)]
    print("a: ",a)
    # list pairs - generates pairs for feeding into each Bigger(X,Y) circuit
    # example - bidders X,Y,Z,W => (X,Y) (X,Z) (X,W) (Y,Z) (Y,W) (Z,W)
    pairs = []
    for i in range(0,len(a)-1):
        for j in range(i+1,len(a)):
            pairs.append([a[i],a[j]])
    print("pairs: ",pairs)
    input_gates = []
    inter_gates = []
    mid_gates = []
    output_gates = []
    # gate_num - maintains gate number for every Bigger circuit
    gate_num = 0
    for i in range(0,len(pairs)):
        input_gate(pairs[i][0], pairs[i][1], input_gates, n, gate_num)
        inter_gate(pairs[i][0], pairs[i][1], inter_gates, gate_num)
        mid_gate(mid_gates, gate_num)
        output_gate(output_gates, gate_num)
        # for inputs of length 2 : size of Bigger(X, Y) = 10 gates
        gate_num += 10 
    
    ckt_len = len(input_gates) + len(inter_gates) + len(mid_gates) + len(output_gates)
    print("Circuit length: ",ckt_len)
    print("-------------------------")
    print("input_gates:\n ",input_gates)
    print("-------------------------")
    print("inter_gates:\n ",inter_gates)
    print("-------------------------")
    print("mid_gates:\n ",mid_gates)
    print("-------------------------")
    print("output_gates:\n ",output_gates)
    print("-------------------------")
    
    N = num_bidders*ip_len 
    # write to json
    j = {
            "num_inputs": N,
            "ip_len": ip_len,
            "on_input_gates": input_gates,
            "mid_gates": mid_gates,
            "inter_gates": inter_gates,
            "output_gates": output_gates 
            
        }

    with open("test/circuit.json",'w') as f:
        json.dump(j,f)

