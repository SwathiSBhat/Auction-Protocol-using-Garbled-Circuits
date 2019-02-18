#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : auction_circuit_gen.py
# Author            : Swathi S Bhat
# Date              : 07.12.2018
# Last Modified Date: 13.12.2018
# Last Modified By  : Swathi S Bhat
from __future__ import print_function

import json 
from termcolor import colored
from halo import Halo

# ip1 = x(i) ip2 = y(i) n = input number of NOT 1 input
def bigger(ip1, ip2, ip_gates, inter_gates, n, gate_num):
    ip_gates.append([gate_num, 'NOT', [ip2, n]])
    inter_gates.append([gate_num + 1, 'AND', [ip1, gate_num], [True, False]])
    # increment gate_num by 2


def equal_ckt(ip1, ip2, ip_gates, mid_gates, n, gate_num):
    ip_gates.append([gate_num, 'NOT', [ip1, n]])
    ip_gates.append([gate_num + 1, 'NOT', [ip2, n]])
    ip_gates.append([gate_num + 2, 'AND', [ip1, ip2]])
    mid_gates.append([gate_num + 3, 'AND', [gate_num, gate_num + 1]])
    mid_gates.append([gate_num + 4, 'OR', [gate_num + 2, gate_num + 3]])
    # increment gate_num by 5

# for all a_k where k from k-2
# for k = k-1 a_k = equal_ckt
# a_k = gate_num of gate outputting a_k vale
# eq  = gate_num of equal_ckt output
def a_ckt(a_k, eq, mid_gates, gate_num):
    mid_gates.append([gate_num, 'AND', [eq, a_k]])
    # increment gate_num by 1

if __name__ == "__main__":
    num_bidders = int(raw_input("Enter number of bidders: "))
    ip_len = int(raw_input("Enter length of bid: "))
    # n = index of input to NOT gate i.e last index
    n = num_bidders*ip_len
    # list a - stores starting bit index for every bidder
    # example - bidders X,Y,Z,W => a = [0, 2, 4, 6]
    # X has bits 01 , Y 23, Z 45, W 67
    a = [i for i in range(0,num_bidders*ip_len,ip_len)]
    # list pairs - generates pairs for feeding into each Bigger(X,Y) circuit
    # example - bidders X,Y,Z,W => (X,Y) (X,Z) (X,W) (Y,Z) (Y,W) (Z,W)
    pairs = []
    for i in range(0,len(a)-1):
        for j in range(i+1,len(a)):
            pairs.append([a[i],a[j]])
    input_gates = []
    mid_gates = []
    inter_gates = []
    output_gates = []
    gate_num = 0


    for i in range(0,len(pairs)):
        # a_k = list to store a_k values
        a_k = []
        # out_index = list to maintain output gate_num of Bigger AND a_k 
        out_index = []
        for j in range(0,ip_len):
            # if first input bit i.e msb, create Bigger(x0,y0)
            if j == 0:
                # pairs[i][0] = point to X in [X,Y]
                # pairs[i][0]+j gives jth bit index of X
                bigger(pairs[i][0]+j,pairs[i][1]+j,input_gates,inter_gates,n,gate_num)
                """
                print("----------------------------")
                print("Bigger({},{}): input gates: {} inter_gates: {}".format(pairs[i][0]+j,pairs[i][1]+j,input_gates,inter_gates))
                print("----------------------------")
                """
                gate_num += 2
                out_index.append(gate_num-1)
            elif j == 1:
                bigger(pairs[i][0]+j,pairs[i][1]+j,input_gates,inter_gates,n,gate_num)
                """
                print("----------------------------")
                print("Bigger({},{}): input gates: {} inter_gates: {}".format(pairs[i][0]+j,pairs[i][1]+j,input_gates,inter_gates))
                print("----------------------------")
                """
                gate_num += 2
                # index of output gate of bigger
                index1 = gate_num - 1
                # ip1 = pairs[i][0]+j-1 = pairs[i][0]
                equal_ckt(pairs[i][0],pairs[i][1],input_gates,mid_gates,n,gate_num)
                """
                print("----------------------------")
                print("Equal({},{}): input gates: {} mid_gates: {}".format(pairs[i][0],pairs[i][1],input_gates,mid_gates))
                print("----------------------------")
                """
                gate_num += 5
                # index of output gate of equal gate
                index2 = gate_num - 1
                # ------ add index2 into a_k list
                a_k.append(index2)
                # add AND gate for output of bigger and equal
                mid_gates.append([gate_num, 'AND', [index1, index2]])
                # add gate_num to out_index list
                out_index.append(gate_num)
                gate_num += 1

            else:
                bigger(pairs[i][0]+j,pairs[i][1]+j,input_gates,inter_gates,n,gate_num)
                """
                print("----------------------------")
                print("Bigger({},{}): input gates: {} inter_gates: {}".format(pairs[i][0]+j,pairs[i][1]+j,input_gates,inter_gates))
                print("----------------------------")
                """
                gate_num += 2
                index1 = gate_num - 1
                equal_ckt(pairs[i][0]+j-1,pairs[i][1]+j-1,input_gates,mid_gates,n,gate_num)
                """
                print("----------------------------")
                print("Equal({},{}): input gates: {} mid_gates: {}".format(pairs[i][0]+j-1,pairs[i][1]+j-1,input_gates,mid_gates))
                print("----------------------------")
                """
                gate_num += 5
                index2 = gate_num - 1
                # ---- add AND gate for a_k+1 and equal result
                # TODO use ak_ckt function
                mid_gates.append([gate_num, 'AND', [a_k[j-2], index2]])
                a_k.append(gate_num)
                gate_num += 1
                # ---- add AND gate for a_k and bigger
                mid_gates.append([gate_num, 'AND', [gate_num - 1, index1]])
                out_index.append(gate_num)
                gate_num += 1
        """
        print("---------------------------")
        print("out_index: {}".format(out_index))
        print("---------------------------")
        """
        gate_num = out_index[-1] + 1
        while len(out_index) > 1:
            if len(out_index) > 2:
                # print("len : {}".format(len(out_index)))
                mid_gates.append([gate_num, 'OR', [out_index[0], out_index[1]]])
                out_index = out_index[2:]
                out_index[:0] = [gate_num]
                gate_num += 1
                # print("out_index: {}".format(out_index))

            else:
                # print("len : {}".format(len(out_index)))
                output_gates.append([gate_num, 'OR', [out_index[0], out_index[1]]])
                out_index = []
                out_index.append(gate_num)
                gate_num += 1
                # print("out_index: {}".format(out_index))


    print(colored("-------------------------------------------------------",'blue'))
    print("Input gates: {} inter_gates: {} mid_gates: {} output_gates:{}".format(input_gates,inter_gates,mid_gates,output_gates))
    print(colored("-------------------------------------------------------",'blue'))
    num_gates = len(input_gates) + len(inter_gates) + len(mid_gates) + len(output_gates)
    spinner = Halo(text="Number of gates: "+str(num_gates), spinner='dots', text_color="green")
    spinner.start()
    spinner.succeed()
    spinner.stop()
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

    with open("test/circuit.json", 'w') as f:
        json.dump(j, f)


