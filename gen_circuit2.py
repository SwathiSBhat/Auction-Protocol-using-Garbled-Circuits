#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : gen_circuit2.py
# Author            : Swathi S Bhat
# Date              : 07.12.2018
# Last Modified Date: 07.12.2018
# Last Modified By  : Swathi S Bhat
from __future__ import print_function

import json 
from random import SystemRandom

"""
Generates circuit having N gates 
in a linear fashion as shown:

---||
   ||---||
---||   ||---||
      --||   ||--- .... 
           --||

"""


def get_gate_type():
    opt = SystemRandom().randint(1,3)
    if opt == 1:
        gate_type = "AND"
    elif opt == 2:
        gate_type = "XOR"
    else:
        gate_type = "OR"
    return gate_type 

def input_gates(N):
    inputs = []
    # adding first gate 
    gate_type = get_gate_type()
    inputs.append([0,gate_type,[0,1]])
    if N == 2:
        return inputs 
    return inputs
    

def inter_gates(N):
    inter = []
    # TODO - Take care of corner cases
    # like N = 2
    for i in range(1, N-1):
        it = []
        it.append(i)
        gate_type = get_gate_type()
        it.append(gate_type)
        it.append([i-1, i+1])
        it.append([False, True])
        inter.append(it)
    return inter 
        

def output_gates(N,gate_type):
    outputs = []
    # gate_type of output gate = gate type of last input gate
    outputs.append([N-2,gate_type,[N-3,N-1]])
    return outputs 

if __name__ == "__main__":
    
    while True:
        try:
            N = int(raw_input("Enter number of inputs: "))
            break 
        except ValueError:
            print("Please enter valid input")
            continue
    
    ip_len = int(raw_input("Enter input length of bids: "))
    if N % ip_len != 0:
        print("Inputs can't be distributed among bidders!")
        exit(0)

    on_input_gates = input_gates(N)
    print("Input gates: ",on_input_gates)
    on_mid_gates = []
    print("Mid gates: ",on_mid_gates)
    on_inter_gates = inter_gates(N)
    print("Inter gates: ",on_inter_gates)
    # last inter gate and output gate are the same
    # hence gate types should match 
    op_gate_type = on_inter_gates[-1][1]
    on_output_gates = output_gates(N, op_gate_type)
    print("Output gates: ",on_output_gates)

    # write to json
    j = {
            "num_inputs": N,
            "ip_len": ip_len,
            "on_input_gates": on_input_gates,
            "mid_gates": on_mid_gates,
            "inter_gates": on_inter_gates,
            "output_gates": on_output_gates 
        }
    with open("test/circuit.json", 'w') as f:
        json.dump(j,f)

