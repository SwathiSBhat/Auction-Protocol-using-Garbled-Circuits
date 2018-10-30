from __future__ import print_function

from cryptography.fernet import Fernet
from random import SystemRandom
import json

cryptorand = SystemRandom()

def shuffle(l):
    for i in range(len(l)-1, 0, -1):
        j = cryptorand.randrange(i+1)
        l[i], l[j] = l[j], l[i]

def keypair():
    '''
    creates a fresh Fernet key pair required as wire labels
    '''
    # DEBUG:
    return {0: Fernet.generate_key(), 1: Fernet.generate_key()}

class Gate(object):

    def keypair(self):
        return keypair()

    # outputs = keypair for the mentioned wire ID
    def grab_wires(self):
        """
        Returns tags for 0/1 for both input wires 
        """
        # print("Grab wires: 0: ",self.circuit.gates[self.inputs[0]].outputs, " \n1: ",self.circuit.gates[self.inputs[1]].outputs)
        return {0: self.circuit.gates[self.inputs[0]].outputs,
                1: self.circuit.gates[self.inputs[1]].outputs}
    
    gate_ref = {
        "AND": (lambda x, y: x and y),
        "XOR": (lambda x, y: x ^ y),
        "OR": (lambda x, y: x or y)
    }
    
    # inputs = list of 2 items containing input wire IDs 
    # ctype = gate type
    def __init__(self, circuit, g_id, gate_type, inputs):
        self.circuit = circuit
        self.g_id = g_id
        self.inputs = inputs
        self.outputs = self.keypair()
            # array of keys for output, [false, true]
        self.table = [] # the garbled output table

        wires = self.grab_wires()

        self.output = None

        f = {}
        for i in (0, 1):
            f[i] = {}
            for j in (0, 1):
                f[i][j] = Fernet(wires[i][j])
    

        for i in range(2):
            for j in range(2):
                if self.gate_ref[gate_type](i, j):
                    enc = f[0][i].encrypt(self.outputs[1])
                    self.table.append(f[1][j].encrypt(enc))
                else:
                    enc = f[0][i].encrypt(self.outputs[0])
                    self.table.append(f[1][j].encrypt(enc))
        
        # DEBUG
        # print("Gate initialization for gate_id: ",self.g_id," inputs: ",self.inputs," outputs: ",self.outputs," wires: ",wires)
        # print("--------------------------------------")
        # print("g_id: ",self.g_id," table: ",self.table)
        # print("--------------------------------------")


        shuffle(self.table) # TODO: make this crypto secure
        

    def grab_inputs(self):
        """
        Gets tags for 0/1 for both input wires in output gate
        i.e tags for 0/1 in input wire1
        and tags for 0/1 in input wire2
        inputs[0] = wire ID of 1st input wire
        inputs[1] = wire ID of 2nd input wire 
        """
        return {0: self.circuit.gates[self.inputs[0]].fire(),
                1: self.circuit.gates[self.inputs[1]].fire()}

    def fire(self):
        if self.output is None:
            keys = self.grab_inputs()
            #print(self.g_id, keys, self.table)

            fs = [Fernet(keys[1]), Fernet(keys[0])]

            decrypt_table = self.table
            
            # DEBUG - to print corresponding key value for ciphertext
            count = 0

            for f in fs:
                new_table = []
                for ciphertext in decrypt_table:
                    dec = None
                    try:
                        dec = f.decrypt(ciphertext)
                        """
                        print("---------------------------")                        
                        # DEBUG 
                        print("Type of ciphertext: ",type(ciphertext))
                        if count==0:
                            print("decrypted: ",dec," ciphertext: ",ciphertext," key: ",keys[1])
                        else:
                            print("decrypted: ",dec," ciphertext: ",ciphertext," key: ",keys[0])

                        print("---------------------------") 
                        """
                    except:
                        pass
                    if dec is not None:
                        new_table.append(dec)
                count += 1        
                decrypt_table = new_table

            print("---------------------------------------")
            print("decrypt table:\n")
            print(decrypt_table)
            print("---------------------------------------")

            if len(decrypt_table) != 1:
                raise ValueError("decrypt_table should be length 1 after decrypting")

            self.output = decrypt_table[0]
            print("output: ",self.output)

        return self.output

class OnInputGate(Gate):

    def __init__(self, circuit, g_id, gate_type, inputs):
        Gate.__init__(self, circuit, g_id, gate_type, inputs)

    def grab_wires(self):
        return {0: self.circuit.poss_inputs[self.inputs[0]],
                1: self.circuit.poss_inputs[self.inputs[1]]}

    def grab_inputs(self):
        return {0: self.circuit.inputs[self.inputs[0]],
                1: self.circuit.inputs[self.inputs[1]]}

class OutputGate(Gate):
    def keypair(self):
        return [bytes([0]), bytes([1])]

    def __init__(self, circuit, g_id, gate_type, inputs, flag, interg):
        self.flag = flag
        self.interg = interg 
        Gate.__init__(self, circuit, g_id, gate_type, inputs)

    def grab_wires(self):
        #print("************")
        #print("self.interg: ",self.interg)
        #print("************")
        if self.flag == True:
            if self.interg[3][0] == True and self.interg[3][1] == False:
                return {0: self.circuit.poss_inputs[self.inputs[0]],
                        1: self.circuit.gates[self.inputs[1]].outputs}
            elif self.interg[3][0] == False and self.interg[3][1] == True:
                return {0: self.circuit.gates[self.inputs[0]].outputs,
                        1: self.circuit.poss_inputs[self.inputs[1]]}
            # TODO : Quit program is ValueError raised
            else:
                raise ValueError("Invalid output gate")
        else: 
            return {0: self.circuit.gates[self.inputs[0]].outputs,
                    1: self.circuit.gates[self.inputs[1]].outputs}
    
    def grab_inputs(self):
        if self.flag == True:
            if self.interg[3][0] == True and self.interg[3][1] == False:
                return {0: self.circuit.inputs[self.inputs[0]],
                        1: self.circuit.gates[self.inputs[1]].fire()}
            elif self.interg[3][0] == False and self.interg[3][1] == True:
                return {0: self.circuit.gates[self.inputs[0]].fire(),
                        1: self.circuit.inputs[self.inputs[1]]}
            else:
                raise ValueError("Invalid Output Gate")
        else: 
            return {0: self.circuit.gates[self.inputs[0]].fire(),
                    1: self.circuit.gates[self.inputs[1]].fire()}



class InterGate(Gate):

    # input type = dict containing {0:True/False, 1:False/True}
    # True = input number is an input wire
    # False = input number is an input gate
    # input_type = {}
    
    def __init__(self, circuit, g_id, gate_type, inputs, input_type):
        self.input_type = input_type
        # print("input_type of INTERMEDIATE GATE: ",input_type)
        Gate.__init__(self, circuit, g_id, gate_type, inputs)

    def grab_wires(self):
        if self.input_type[0] == True and self.input_type[1] == False:
            return {0: self.circuit.poss_inputs[self.inputs[0]],
                    1: self.circuit.gates[self.inputs[1]].outputs}
        elif self.input_type[0] == False and self.input_type[1] == True:
            return {0: self.circuit.gates[self.inputs[0]].outputs,
                    1: self.circuit.poss_inputs[self.inputs[1]]}
        # TODO : Quit program is ValueError raised
        else:
            raise ValueError("Invalid Intermediate Gate")

    def grab_inputs(self):
        if self.input_type[0] == True and self.input_type[1] == False:
            return {0: self.circuit.inputs[self.inputs[0]],
                    1: self.circuit.gates[self.inputs[1]].fire()}
        elif self.input_type[0] == False and self.input_type[1] == True:
            return {0: self.circuit.gates[self.inputs[0]].fire(),
                    1: self.circuit.inputs[self.inputs[1]]}
        else:
            raise ValueError("Invalid Intermediate Gate")
    

class Circuit(object):

    def __init__(self, num_inputs, on_input_gates, mid_gates, inter_gates, output_gates):
        # num_inputs = no. of input wires
        # poss_inputs = generates labels for 0 and 1 for each wire
        self.num_inputs = num_inputs
        self.poss_inputs = [keypair() for x in range(num_inputs)]
        self.gates = {}

        for g in on_input_gates:
            # g[0] = gate_id , g[1] = gate_type , g[2] = array with input wire ids
            self.gates[g[0]] = OnInputGate(self, g[0], g[1], {0: g[2][0], 1: g[2][1]})

        for g in mid_gates:
            self.gates[g[0]] = Gate(self, g[0], g[1], {0: g[2][0], 1: g[2][1]})

        # DEBUG 
        for g in inter_gates:
            self.gates[g[0]] = InterGate(self, g[0], g[1], {0: g[2][0], 1: g[2][1]}, {0: g[3][0], 1: g[3][1]})

        self.output_gate_ids = []
        for g in output_gates:
            self.output_gate_ids.append(g[0])
            flag = False
            interg = []
            # condition to check if output_gate = inter_gate
            # if yes, grab_wires should be changed for output_gate
            if g[0] in [x[0] for x in inter_gates]:
                flag = True
                interg = x
                # print("************")
                # print("interg: ",interg)
                # print("************")
            self.gates[g[0]] = OutputGate(self, g[0], g[1], {0: g[2][0], 1: g[2][1]}, flag, interg)
       
        # DEBUG 
        # print("Gates: ",self.gates[0])
        # print("Possible inputs: ",self.poss_inputs)

    # Returns dict with o/p gate id as key and corresponding value
    # inputs = chosen wire labels to be used for computation
    def fire(self, inputs):
        self.inputs = inputs
        output = {}
        for g_id in self.output_gate_ids:
            output[g_id] = self.gates[g_id].fire()
        return output

    def prep_for_json(self):
        j = {"num_inputs": self.num_inputs,
                "on_input_gates": {},
                "inter_gates": {},
                "gates": {},
                "output_gate_ids": self.output_gate_ids}
        
        for g_id, gate in self.gates.items():
            # print("-----------------------------")
            # print("gate id: {} gate type: {}".format(g_id,type(gate)))
            gate_json = {"table": gate.table, "inputs": gate.inputs}
            if type(gate) is OnInputGate:
                j["on_input_gates"][gate.g_id] = gate_json
            
            #DEBUG
            # include gates of type OutputGate but are also InterGate
            # TODO: clean code - rename interg to input_type
            elif (type(gate) is InterGate) or (type(gate) is OutputGate and gate.flag == True) :
                if type(gate) == InterGate:
                    gate_json = {"table": gate.table, "inputs": gate.inputs, "intergateinfo": gate.input_type}
                else:
                    # print("********************")
                    # print("interg[0] ",gate.interg[3][0],"interg[1]: ",gate.interg[3][1])
                    # print("********************")
                    input_type = {0: gate.interg[3][0], 1: gate.interg[3][1] }
                    gate_json = {"table": gate.table, "inputs": gate.inputs, "intergateinfo": input_type}
                    # add OutputGate to gates json
                    j["gates"][gate.g_id] = gate_json 
                
                j["inter_gates"][gate.g_id] = gate_json 

            else:
                j["gates"][gate.g_id] = gate_json

        with open('test/garbled_circuit.json','w') as f:
            json.dump(j,f)
        

    def prep_for_json_cut_n_choose(self, filename):
        
        j = {"num_inputs": self.num_inputs,
                "on_input_gates": {},
                "inter_gates": {},
                "gates": {},
                "output_gate_ids": self.output_gate_ids}
        for g_id, gate in self.gates.items():
            gate_json = {"table": gate.table, "inputs": gate.inputs}
            if type(gate) is OnInputGate:
                j["on_input_gates"][gate.g_id] = gate_json
            elif (type(gate) is InterGate) or (type(gate) is OutputGate and gate.flag == True) :
                if type(gate) == InterGate:
                    gate_json = {"table": gate.table, "inputs": gate.inputs, "intergateinfo": gate.input_type}
                else:
                    input_type = {0: gate.interg[3][0], 1: gate.interg[3][1] }
                    gate_json = {"table": gate.table, "inputs": gate.inputs, "intergateinfo": input_type}
                    # add OutputGate to gates json
                    j["gates"][gate.g_id] = gate_json 
                j["inter_gates"][gate.g_id] = gate_json 
                 
            else:
                j["gates"][gate.g_id] = gate_json

        with open("test/"+filename,'a') as f:
            json.dump(j,f)
            f.write("\n")
    

if __name__ == "__main__":
    on_input_gates = [[0, "XOR", [0, 1]]]
    mid_gates = []
    inter_gates = [[1, "AND", [0, 2], [False, True]], [2, "OR", [1, 3], [False, True]]    , [3, "AND", [2, 4], [False, True]], [4, "AND", [3, 5], [False, True]], [5, "AND", [4, 6], [False, True]]]
    output_gates = [[5, "AND", [4, 6]]]
    mycirc = Circuit(7, on_input_gates, mid_gates, inter_gates, output_gates)
    my_input = [x[y] for x, y in zip(mycirc.poss_inputs, [1, 0, 1, 0, 1, 0, 1])]
    mycirc.fire(my_input)
    print("Possible inputs: ",mycirc.poss_inputs)
    mycirc.prep_for_json()
