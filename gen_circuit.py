from __future__ import print_function

import math
import json 
from util import * 

def Log2(x):
    return (math.log10(x) / math.log10(2))

def isPowerofTwo(n):
    return (math.ceil(Log2(n)) == math.floor(Log2(n))) 

def input_gates(N,gate_type):
    inputs = []
    for i,j in zip(range(0,N/2),range(0,N,2)):
        ip = []
        ip.append(i)
        ip.append(gate_type)
        ip.append([j,j+1])
        inputs.append(ip)
    return inputs 

def mid_gates(N,gate_type):
    mid = []
    j = 0 
    for i in range(N/2,N-2):
        m = []
        m.append(i)
        m.append(gate_type)
        m.append([j,j+1])
        j += 2
        mid.append(m)
    return mid 

def out_gates(N,gate_type):
    out = []
    op = []
    op.append(N-2)
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
    
    gate_type = "AND"
    on_input_gates = input_gates(N,gate_type)
    print("Input gates: \n",on_input_gates)
    on_mid_gates = mid_gates(N,gate_type)
    print("Mid gates: \n",on_mid_gates)
    if N == 2:
        on_output_gates = on_input_gates
    else:
        on_output_gates = out_gates(N,gate_type)
    print("Output gates: \n",on_output_gates)

    # write to json
    j = {
            "num_inputs": N,
            "on_input_gates": on_input_gates,
            "mid_gates": on_mid_gates,
            "output_gates": on_output_gates 
        }
    with open("test/circuit.json", 'w') as f:
        json.dump(j,f)

