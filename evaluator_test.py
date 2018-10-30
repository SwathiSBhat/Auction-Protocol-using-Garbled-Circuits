from __future__ import print_function

from cryptography.fernet import Fernet
import random
import json
class Gate(object):

    def __init__(self, circuit, g_id, gate_json, flag, input_type):
        self.circuit = circuit
        self.g_id = g_id
        self.flag = flag
        self.ip_type = input_type 
        self.inputs = {0: gate_json["inputs"]["0"],
                       1: gate_json["inputs"]["1"]}
        # self.table = [bytes(bytearray(t["__value__"])) for t in gate_json["table"]] # the garbled output table

        self.table = [t for t in gate_json["table"]]
        self.output = None

    def grab_inputs(self):
        
        # DEBUG
        #print("---------------------------")
        #print("circuit gate id: ",self.g_id,"type of gate: ",type(self))
        #print("ip_type: ",self.ip_type) 
        #print("---------------------------")

        if self.flag == True:
            #print("ip_type[0] ",self.ip_type[0]," ip_type[1] ",self.ip_type[1])
            if self.ip_type[0] == True and self.ip_type[1] == False:
                return {0: self.circuit.inputs[self.inputs[0]],
                        1: self.circuit.gates[self.inputs[1]].fire()}
            elif self.ip_type[0] == False and self.ip_type[1] == True:
                return {0: self.circuit.gates[self.inputs[0]].fire(),
                        1: self.circuit.inputs[self.inputs[1]]}
            else:
                return {0: self.circuit.gates[self.inputs[0]].fire(),
                        1: self.circuit.gates[self.inputs[1]].fire()}
        else:
            key0 = self.circuit.gates[self.inputs[0]].fire()
            key1 = self.circuit.gates[self.inputs[1]].fire()
            # print("Fernet keys: key0: ",key0," key1:  ",key1)
            # print("---------------------------")
            return {0: self.circuit.gates[self.inputs[0]].fire(),
                    1: self.circuit.gates[self.inputs[1]].fire()}

    def fire(self):
        if self.output is None:
            keys = self.grab_inputs()
            
            #print("---------------------------")
            #print(self.g_id, keys, self.table)
            #print(keys)
            #print("---------------------------")
            
            fs = [Fernet(keys[1]), Fernet(keys[0])]
            """
            print("Fernet keys: k0: {} k1: {}".format(keys[0],keys[1]))
            print("---------------------------")
            """
            decrypt_table = self.table

            # DEBUG 
            count = 0

            for f in fs:
                new_table = []
                for ciphertext in decrypt_table:
                    ciphertext = str(ciphertext)
                    dec = None
                    """
                    if count == 0:
                        print("decrypted: ",dec," ciphertext: ",ciphertext," key: ",keys[1])
                    else:
                        print("decrypted: ",dec," ciphertext: ",ciphertext," key: ",keys[0])
                    """
                    try:
                        dec = f.decrypt(ciphertext)

                        #DEBUG
                        """
                       if count==0:
                            print("decrypted: ",dec," ciphertext: ",ciphertext," key: ",keys[1])
                        else:
                            print("decrypted: ",dec," ciphertext: ",ciphertext," key: ",keys[0])
                        """
                    except:
                        pass
                    if dec is not None:
                        new_table.append(dec)
                count += 1
                decrypt_table = new_table
            print("-------------------------------")
            print("decrypted table: \n")
            print(decrypt_table)
            print("-------------------------------")

            if len(decrypt_table) != 1:
                raise ValueError("decrypt_table should be length 1 after decrypting")

            self.output = decrypt_table[0]
            # print("output: ",self.output)

        return self.output

class OnInputGate(Gate):
    def __init__(self, circuit, g_id, gate_json):
        Gate.__init__(self, circuit, g_id, gate_json, False, [])

    def grab_inputs(self):
        return {0: self.circuit.inputs[self.inputs[0]],
                1: self.circuit.inputs[self.inputs[1]]}

class InterGate(Gate):
    def __init__(self, circuit, g_id, gate_json, input_type):
        self.input_type = input_type 
        # TODO : create outputGate class and remove last 2 args from Gate
        Gate.__init__(self, circuit, g_id, gate_json, False, [])

    def grab_inputs(self):
        if self.input_type[0] == True and self.input_type[1] == False:
            return {0: self.circuit.inputs[self.inputs[0]],
                    1: self.circuit.gates[self.inputs[1]].fire()}
        elif self.input_type[0] == False and self.input_type[1] == True:
            return {0: self.circuit.gates[self.inputs[0]].fire(),
                    1: self.circuit.inputs[self.inputs[1]]}

class Circuit(object):
    def __init__(self, circuit_json):
        self.num_inputs = circuit_json["num_inputs"]
        self.gates = {}

        for g_id, g in circuit_json["on_input_gates"].items():
            self.gates[int(g_id)] = OnInputGate(self, g_id, g)
        
        #DEBUG
        #print "*******************************"
        #print "circuit_json: ",circuit_json["inter_gates"].items()
        #print "*******************************"
        #print "len(items): ",len(circuit_json["inter_gates"].items())
        
        for g_id, g in circuit_json["inter_gates"].items():
            # print("g_id: ",g_id)
            # keys and values of input_type dict is str when loaded from json
            # convert key to int
            input_type = g['intergateinfo']
            input_type = {int(k):v for k,v in input_type.items()}
            self.gates[int(g_id)] = InterGate(self, g_id, g, input_type)
            # print("g_id: ",g_id," g:  ",g," input_type ",input_type)  

        for g_id, g in circuit_json["gates"].items():
            # check if output gate is inter gate also
            # if yes then grab_inputs must be different
            flag = False 
            input_type = {} 
            if int(g_id) in [int(gate_id) for gate_id in circuit_json["inter_gates"] ]:
                # print("**********************************")
                # print("g_id ",g_id)
                # print("**********************************")
                flag = True 
                input_type = circuit_json["inter_gates"][g_id]['intergateinfo']
                input_type = {int(k):v for k,v in input_type.items()}
                # print("******************************")
                # print("input_type: ",input_type)
            
            self.gates[int(g_id)] = Gate(self, g_id, g, flag, input_type)

        self.output_gate_ids = circuit_json["output_gate_ids"]

    def fire(self, inputs):
        self.inputs = inputs
        output = {}
        # print(self.output_gate_ids)
        # print(self.gates)
        for g_id in self.output_gate_ids:
            output[g_id] = self.gates[g_id].fire()
        return output

if __name__ == "__main__":

    with open('json_circuit.json') as data_file:    
        data = json.load(data_file)
    
    mycirc = Circuit(data)
    inputs =[
            b'uyo3gJxKVVwCPPQD_r6v-eO0V05Ty9-dMFFH0Kbyx-Q=',
            b'd0kQRE0xysf1G0rJXIDc_GzKXJumCCaETxAYKXLoGDw=',
            b'IFoY_1AluwcIkp9PgTQoMtzLilbButGLIChxCAs3-84=',
            b'K3earsJFmHQWAgr-63rATclBcNd77Z1gO9820ejNjWo='
            ]
    print(mycirc.fire(inputs))

