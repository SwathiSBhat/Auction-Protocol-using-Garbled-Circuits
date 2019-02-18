#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : GM.py
# Author            : Swathi S Bhat
# Date              : 13.12.2018
# Last Modified Date: 13.12.2018
# Last Modified By  : Swathi S Bhat
from __future__ import print_function

import sys
import util
import random 

def GM_keygen(bit_size):
    """
    GM key generation
    """
    # TODO: Bug: while generating prime if p<n-2 
    # miller rabin randint gives error as randint(a,b) a>b

    p = util.generate_rsa_prime(bit_size)
    q = util.generate_rsa_prime(bit_size)
    
    # TODO: Add primes of type p=1mod3 that have 3 cube roots
    # Note- primes of type 2mod3 are chosen as cube root 
    # calculation is efficient
    while(p%3!=2):
        p = util.generate_rsa_prime(bit_size)
    while(q%3!=2):
        q = util.generate_rsa_prime(bit_size)
    
    while(p==q):
        p = util.generate_rsa_prime(bit_size)

    #print("P: ",p," q: ",q)
    N = p*q

    """
    Finding x such that jacobi(x,p)=-1 and jacobi(x,q)=-1
    """
    a,b=0,0
    while util.jacobi(a,p)!=-1:
        a = random.SystemRandom().randint(1,p)
    # print("Found a! : ",a)
    while util.jacobi(b,q)!=-1: 
        b = random.SystemRandom().randint(1,q)
    # print("Found b! : ",b)
    x = util.crt([a,b],[p,q])

    pub_key = (x,N)
    priv_key = (p,q)

    return pub_key,priv_key


def GM_encrypt(msg,pub_key):
    """
    GM message encryption
    """
    x,N = pub_key[0],pub_key[1]
    # msg_binary = format(msg,'b')

    """
    Generating random y_i for every bit in m 
    such that gcd(y_i,N)=1
    """
    count=0
    y = []
    while count<len(msg):
        yi = random.SystemRandom().randint(1,N-1)
        if util.gcd(yi,N)==1:
            count+=1
            y.append(yi)
    
    c=[]
    for i in range(0,len(msg)):
        c_i = (pow(y[i],2)*pow(x,int(msg[i],2)))%N
        c.append(c_i)

    """
    Homomorphic property: 
    Note that the values for E[c0].E[c1] may not be
    equal to E[m0^m1]. It just gives both the answers
    as either QRs or QNR.
    """
    
    return c

def GM_decrypt(c,priv_key):
    """
    GM message decryption
    """
    p,q=priv_key[0],priv_key[1]

    msg=""
    for i in c:
        if util.jacobi(i,p)==1 and util.jacobi(i,q)==1:
            msg+='0'
        else:
            msg+='1'
    
    #msg = int(msg,2)

    return msg 

if __name__=="__main__":
    bit_size = int(raw_input("Enter bit size for primes p,q: "))
    pub_key,priv_key=GM_keygen(bit_size)
    print("Pub_key(x,N): ",pub_key," Priv_key(p,q): ",priv_key)
    # TODO: Handle case where input message is an integer
    msg = raw_input("Enter message to encrypt: ")
    # TODO: In case message is just a bot string,below line not required
    # msg = util.convert_to_binstr(msg)
    print("Message to encrypt: ",msg)
    c=GM_encrypt(msg,pub_key)
    print("Encrypted message: ",c)
    m=GM_decrypt(c,priv_key)
    print("Decrypted message: ",m)
    # m=util.convert_to_str(m)
    # print("Decrypted string: ",m)






    
    
