from __future__ import print_function

import socket
import threading
import GM  
from commitment import Double_Commitment 
import random 
import hashlib 
import json 
import util
import cuberoot 
import garbler  

#variables
MAX_DATA_RECV = 999999

class ProxyThread(threading.Thread):

    def __init__(self, proxyaddr, proxysock):
        threading.Thread.__init__(self)
        self.proxy_socket = proxysock
        print("New proxy connection made at: ", proxyaddr)

    def run(self):
        """
        VPOT
        """
        
        # creation of RSA modulus n by Sender i.e n=p*q
        # TODO: check for bit size for RSA primes
        # TODO: check if this n is the same as that used in GM
        pub_key,priv_key = GM.GM_keygen(12)
        N = pub_key[1]
        p,q = priv_key[0],priv_key[1]
        
        # 0. Send number of bidders to proxy 
        # Proxy sends connection number to sender so that
        # sender can initialize corresponding tags
        data = json.dumps({"count":CONN_COUNT})
        self.proxy_socket.send(data.encode())
        data = self.proxy_socket.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        # connection count received from proxy
        count = data.get("conn_count")
        print("Received conn_count {} from proxy",count)
        # TODO: Add method to end if count > CONN_COUNT
        if count > CONN_COUNT:
            print("Number of bidders can't be greater than number of inputs")
        print("---------------------------------")

        # 1. Sender chooses tags t0,t1 and an integer C  
        tags = []
        print("CONN_COUNT: ",count)
        try:
            t0 = mycirc.poss_inputs[count-1][0]
            t1 = mycirc.poss_inputs[count-1][1]
            print("Tag0: {} Tag1: {}".format(t0,t1))
            tags.append(t0)
            tags.append(t1)
        except(IndexError):
            raise ValueError("Number of bidders can't be greater than no of inputs")

        print("---------------------------------")

        while True:
            C = random.SystemRandom().randint(1,N-1)
            if util.gcd(C,N)==1:
                break

        # 2. Sender computes commitmentsand ordering a
        # Also computes u = E[a] and CO = Hash(u)
        # Transmit (C0,C1), CO to proxy
        a = random.SystemRandom().getrandbits(1)
        print("a: ",a)
        # generating witnesses k0 and k1 for computing commitments
        k =[]
        k.append(random.SystemRandom().randint(1,N-1))
        k.append(random.SystemRandom().randint(1,N-1))
        # DEBUG
        print("k0: {} k1: {}".format(k[0],k[1]))

        C0 = Double_Commitment(k[a],tags[a],N).commitment
        C1 = Double_Commitment(k[1-a],tags[1-a],N).commitment

        # TODO: u is a list returned by GM_encrypt
        u = GM.GM_encrypt(str(a),pub_key)
        u_str = ''.join(str(x) for x in u)
        CO = hashlib.sha256(u_str).hexdigest()

        data = json.dumps({"pub_key":pub_key, "C":C, "C0":C0, "C1":C1, "u":u, "CO":CO})
        print("-------------------------------------")
        print("Sent pub_key:{}, (C0,C1):({},{}), u: {}, CO:{} to proxy".format(pub_key,C0,C1,u_str,CO))
        print("-------------------------------------")
        self.proxy_socket.send(data.encode())

        # TODO: Send bs directly from chooser
        # 5. Sender receives x0 from proxy and computes x1=x0*C
        # y0 = x0^1/3 y1 = x1^1/3. Sender decrypts bs
        # if bs=0 transmit (z0,z1)=(y0k0,y1k1) to proxy else (y0k1,y1k0)
        # Send u to proxy 

        v_list = []
        data = self.proxy_socket.recv(MAX_DATA_RECV)
        data = json.loads(data.decode())
        x0,v = data.get("x0"),data.get("v")
        v_list.append(int(v))
        print("Received x0: {} v: {} from proxy".format(x0,v_list))
        
        x0 = x0%N
        x1 = (x0*C)%N
        # TODO: check if it is always a cube root
        # TODO: incorporate hardness to find cube root here
        y = []
        y0 = cuberoot.cuberoot_util(x0,p,q)
        y1 = cuberoot.cuberoot_util(x1,p,q)
        print("Cube root y0: ",y0," y1: ",y1)
        y.append(y0)
        y.append(y1)

        bs = int(GM.GM_decrypt(v_list,priv_key))
        print("Decrypted bs: ",bs," type(bs): ",type(bs))
        

        z = []
        if bs==0:
            z0,z1 = (y[0]*k[0])%N,(y[1]*k[1])%N
            # print("z0=y0k0: ",z0," z1=y1k1: ",z1)
        else:
            z0,z1 = (y[0]*k[1])%N,(y[1]*k[0])%N
            # print("z0=y0k1: ",z0," z1=y1k0: ",z1)
        # TODO: make cleaner code: send z instead of z0,z1
        z.append(z0)
        z.append(z1)

        data = json.dumps({"z0":z0, "z1":z1, "u":u_str})
        self.proxy_socket.send(data.encode())
        print("Sent u: {} z0: {} z1: {} to proxy".format(u_str,z0,z1))

        # Sender reveals c=a^bs by decommitting uv=E[a]E[bs]=E[c]
        # print("u[0]: {} type:u[0]: {} v: {} type(v): {}".format(u[0],type(u[0]),v,type(v)))
        uv = u[0]*v_list[0]
        uvlist = []
        uvlist.append(uv)
        # print("uv_list: ",uvlist)
        c = GM.GM_decrypt(uvlist,priv_key)
        
        data = json.dumps({"c":c })
        self.proxy_socket.send(data.encode())
        print("Sent c:{} to proxy".format(c))

        print("-------------------------------------")
       

# *----- SENDER ------*

CONN_COUNT = int(raw_input("Enter of number of bidders: "))

# TODO: Make entering of circuit from file or dynamic
on_input_gates = [[0, "AND", [0, 1]], 
                [1, "XOR", [2, 3]], 
                [2, "OR", [0,3]]]

mid_gates = [[3, "XOR", [0, 1]],
             [4, "OR", [1, 2]]]

output_gates = [[5, "OR", [3, 4]]]
mycirc = garbler.Circuit(4, on_input_gates, mid_gates, output_gates)
print("Possible input tags: ",mycirc.poss_inputs)
print("----------------------------------------")

# TODO :Make this quit program
if mycirc.num_inputs != CONN_COUNT:
    raise ValueError("Number of inputs to circuit and bidders don't match!")

mycirc.prep_for_json()

sender_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

sender_server.bind(('',0))


# allow sender server to spawn several threads when proxy connects with new client
print("Sender server started at : ",sender_server.getsockname())

while True:
    sender_server.listen(1)
    proxysock, proxyaddr = sender_server.accept()
    newthread = ProxyThread(proxyaddr,proxysock)
    newthread.start()


