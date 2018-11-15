from __future__ import print_function

import util
import random 


#assumes p prime returns cube root of a mod p
def cuberoot(a, p):
    if p == 2:
        return a
    if p == 3:
        return a
    if (p%3) == 2:
        return pow(a,(2*p - 1)/3, p)
    if (p%9) == 4:
        root = pow(a,(2*p + 1)/9, p)
        if pow(root,3,p) == a%p:
            return root
        else:
            return None
    if (p%9) == 7:
        root = pow(a,(p + 2)/9, p)
        if pow(root,3,p) == a%p:
            return root
        else:
            return None
    else:
        print("Not implemented yet.")


def cuberoot_util(a, p, q):
    m = []
    n = []
    n.append(p)
    n.append(q)
    m.append(cuberoot(a,p))
    m.append(cuberoot(a,q))
    # print("a: {} prime p: {} q: {} m: {}".format(a,p,q,m))
    soln = util.crt(m,n)
    return soln 


if __name__=="__main__":
    p = util.generate_rsa_prime(4)
    q = util.generate_rsa_prime(4)
    while(True):
        if p%3!=2:
            p = util.generate_rsa_prime(4)
        else:
            break
    while(True):
        if q%3!=2:
            q = util.generate_rsa_prime(4)
        else:
            break
    while(True):
        if p==q:
            p = util.generate_rsa_prime(4)
        else:
            break 
    p,q = 11,5
    N = p*q
    # selecting a
    a = random.SystemRandom().randint(1,N-1)
    a = 51
    print("p:{} q:{} N:{} a:{}".format(p,q,N,a))
    m = []
    n = []
    n.append(p)
    n.append(q)
    m1 = cuberoot(a,p)
    m2 = cuberoot(a,q)
    m.append(m1)
    m.append(m2)

    soln = util.crt(m,n)
    print("Cube root: ",soln)

if __name__ == "__main__":
    a = 1433402
    p = 3343
    q = 2849
    print("cuberoot({},{}) = {}".format(a,p,cuberoot(a,p)))
