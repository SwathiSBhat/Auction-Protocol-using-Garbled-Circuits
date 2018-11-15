from __future__ import print_function

# cryptographically secure random library for python 3.6+
# import secrets
from random import SystemRandom
import hashlib 
from util import *
import gc_util 

class Double_Commitment():
    
    # commitment object Ck(t) = (Y1,Y2)

    def __init__(self, witness_k, tag, modulus):
        
        # TODO : Make witness_k and tag private
        self.witness_k = witness_k
        self.tag = tag
        self.modulus = modulus
        
        # tag_int = int(''.join(format(ord(x),'b') for x in self.tag),2)
        tag_int = gc_util.encode_str(self.tag)

        m = pow(self.witness_k,3,self.modulus)
        Y1 = hashlib.sha256(format(m,'b')).hexdigest()
        
        # DEBUG
        #print("-------------------")
        #print("Comm[0]: {} Tag: {}, Tag_int: {}".format(Y1,tag,tag_int))
        #print("-------------------")

        witness_k_hash = hashlib.sha256(format(self.witness_k,'b')).hexdigest()
        # DEBUG:
        #print("k: {} ------- hash_k : {}".format(witness_k,witness_k_hash))

        Y2 = int(witness_k_hash,16)^tag_int  
        #print("Comm:---- {}".format(Y2))
        #print("-------------------")
        
        # commitment Ck(tag) = (Y1,Y2)
        # TODO : Convert Y1 and Y2 to same type
        self.commitment = (Y1,Y2)
        
    def __str__(self):
        return "witness_k: {}, tag: {}, commitment: {}".format(self.witness_k, self.tag,self.commitment)

    def open_commitment(self):
        witness_k_hash = hashlib.sha256(format(self.witness_k,'b')).hexdigest()
        tag = self.commitment[1]^int(witness_k_hash,16)
        return tag 

    # add method to verify commitment
    # def verify_commitment():
    





if __name__ == "__main__":
    # TODO : Generate witness_k according to security requirements
    # SystemRandom generates random float between 0.0 and 1.0
    witness_k = int(SystemRandom().random()*1000)
    print("witness_k generated: ",witness_k) 
    comm = Double_Commitment(witness_k,b'4diGEaU1jdM3Pu-BJNSP9g7_QPc4ujAzGxl2BGoVG0M=',23)
    print("Commitment object: ",str(comm))
    print("Opened commitment: ",comm.open_commitment())



