#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : proxy_gen_indices.py
# Author            : Swathi S Bhat
# Date              : 11.12.2018
# Last Modified Date: 12.12.2018
# Last Modified By  : Swathi S Bhat

from __future__ import print_function

import random 
import json 
import sys
from termcolor import colored 

if __name__ == "__main__":
    
    try:
        CONN_COUNT = int(sys.argv[1])
        n = int(sys.argv[2])
    except IndexError:
        print(colored("Usage:",'green'),colored("arg1: num_inputs arg2: num_circuits","red"))
        exit(0)

    #CONN_COUNT = int(raw_input("Enter num_inputs: "))
    #n = int(raw_input("Enter number of circuits: "))
    # send inputs for which commitments are needed
    inputs = []
    for i in range(0, CONN_COUNT):
        inputs.append(random.SystemRandom().getrandbits(1))
    print("Inputs to circuits: ",inputs)
    # data = json.dumps({"inputs":inputs})
    data = {"inputs":inputs}
    with open('json/inputs.json','w') as f:
        json.dump(data, f)
    # s.send(data.encode())
        
    # TODO: Send number of circuits = n from sender to proxy
    num_of_indices = n/2
    # indices = indices of chosen circuits to open
    indices = random.SystemRandom().sample(range(0,n), num_of_indices)
    indices.sort()
    print("Sampled indices: ",indices)

    # data = json.dumps({"indices":indices})
    data = {"indices":indices}
    with open('json/indices.json','w') as f:
        json.dump(data, f)
