from __future__ import print_function

import math
import json 
from util import * 
from random import SystemRandom 
"""
Generates circuit having 2**(N-1)-1 gates
in a tree fashion:

---||
   ||--
---||  |_||
        _||--- ..... 
---||  | ||
   ||--
---||

"""


def Log2(x):
    return (math.log10(x) / math.log10(2))

def isPowerofTwo(n):
    return (math.ceil(Log2(n)) == math.floor(Log2(n))) 

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
    for i,j in zip(range(0,N/2),range(0,N,2)):
        ip = []
        ip.append(i)
        gate_type = get_gate_type()
        # DEBUG
        # gate_type = "OR"
        ip.append(gate_type)
        ip.append([j,j+1])
        inputs.append(ip)
    return inputs 

def mid_gates(N):
    mid = []
    j = 0 
    for i in range(N/2,N-2):
        m = []
        m.append(i)
        gate_type = get_gate_type()
        # DEBUG
        # gate_type = "OR"
        m.append(gate_type)
        m.append([j,j+1])
        j += 2
        mid.append(m)
    return mid 

def out_gates(N):
    out = []
    op = []
    op.append(N-2)
    gate_type = get_gate_type()
    # DEBUG
    # gate_type = "OR"
    op.append(gate_type)
    op.append([N-4,N-3])
    out.append(op)
    return out 

if __name__ == "__main__":
    
    while True:
        try:
            N = int(raw_input("Enter number of inputs: (in powers of 2) "))
            if isPowerofTwo(N) == False:
                print("Number is not a power of 2")
                raise ValueError
            else:
                break
        except ValueError:
            continue 
    
    if N == 1: 
        raise ValueError("Invalid input")
        exit(0)
    
    on_input_gates = input_gates(N)
    print("Input gates: \n",on_input_gates)
    on_mid_gates = mid_gates(N)
    print("Mid gates: \n",on_mid_gates)
    on_inter_gates = []
    if N == 2:
        on_output_gates = on_input_gates
    else:
        on_output_gates = out_gates(N)
    print("Output gates: \n",on_output_gates)

    # write to json
    j = {
            "num_inputs": N,
            "on_input_gates": on_input_gates,
            "mid_gates": on_mid_gates,
            "inter_gates": on_inter_gates,
            "output_gates": on_output_gates 
        }
    with open("test/circuit.json", 'w') as f:
        json.dump(j,f)

