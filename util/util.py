#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : util.py
# Author            : Swathi S Bhat
# Date              : 07.12.2018
# Last Modified Date: 09.12.2018
# Last Modified By  : Swathi S Bhat
import random
import binascii

def convert_to_binstr(msg):
    return bin(int(binascii.hexlify(msg),16))[2:]
    # return ''.join(format(ord(x), 'b') for x in msg)

def convert_to_str(bin_str):
    # TODO: Doesn't work if string has spaces
    return binascii.unhexlify(hex(int(bin_str,2))[2:])

def int_to_bin(n, size):
    """
    converts input integer bid to binary with length = bid length
    """
    n_bin = bin(n)[2:]
    if len(n_bin) < size:
        n_bin = n_bin.zfill(size)
    return n_bin 

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def exteuclid(a, b):
    s, old_s = 0, 1
    t, old_t = 1, 0
    r, old_r = b, a
    while r != 0:
        quotient = old_r/r
        old_r, r = r, old_r-quotient*r
        old_s, s = s, old_s-quotient*s
        old_t, t = t, old_t-quotient*t
    """
    Returns gcd(a,b) and bezout's co-efficients
    """
    return old_r, old_s, old_t

def inverse_modulo(a,n):
    if a==0:
        raise ZeroDivisionError('Division by zero')

    if a<0:
        return n-inverse_modulo(-a,n)

    t=0;new_t=1
    r=n;new_r=a;
    while new_r != 0:
        quotient = r/new_r
        t,new_t = new_t, t-quotient*new_t
        r,new_r = new_r, r-quotient*new_r 
    if r>1:
        raise ValueError('{} has no multiplicative modulo {}'.format(a,n))
    if t<0:
        t = t+n
    return t

def modular_div_util(x,a,n):
    """ 
    Returns (x/a)modn 
    """
    t = x*inverse_modulo(a,n)
    return t%n


def miller_rabin(n, k=20):
    # TODO: cover all corner cases
    d = n-1
    r = 0
    while(d % 2 == 0):
        d /= 2
        r += 1
    for i in range(0, k, 1):
        a = random.SystemRandom().randint(2, n-2)
        x = pow(a, d, n)
        if x == 1 or x == n-1:
            continue
        for j in range(0, r-1, 1):
            x = (x*x) % n
            if x == 1:
                return False
            if x == n-1:
                break
        if x == n-1:
            continue
        return False
    return True


def jacobi(a, b):
    """ 
    Function to compute Jacobi symbol
    """
    if b <= 0 or b % 2 == 0:
        return 0

    j = 1

    if a < 0:
        a = -a
        if b % 4 == 3:
            j = -j
    while a != 0:
        while not a % 2:
            a /= 2
            if b % 8 == 3 or b % 8 == 5:
                j = -j
        a, b = b, a
        if a % 4 == 3 and b % 4 == 3:
            j = -j
        a = a % b
    if b == 1:
        return j
    else:
        return 0


def crt(a, n):
    """ 

    Function that returns solutions to equations:
    x = a[1]mod(n[1])
    .
    .
    x = a[k]mod(n[k])
    using CRT

    reference : https://brilliant.org/wiki/chinese-remainder-theorem/

    """
    # multiplies every pair of elements from n[1] to n[k] to obtain N
    N = reduce(lambda a, b: a*b, n)

    multipliers = []
    for n_i in n:
        y_i = N/n_i
        gcd, z_i, y = exteuclid(y_i, n_i)
        multipliers.append(z_i*y_i % N)

    result = 0
    for multi, a_i in zip(multipliers, a):
        result = (result+multi*a_i) % N
    return result


def generate_rsa_prime(bit_size):
    p = random.SystemRandom().randint(2**(bit_size-1), 2**(bit_size))
    if not p & 1:
        p = p + 1
    # note - generating only primes p where p % 3 == 2
    # else there are cases when cube roots don't exist
    while miller_rabin(p) == False or (miller_rabin(p) == True and p%3!=2):
        p = p + 2
    return p


if __name__ == "__main__":
    print "Prime of length 30 bits: ", generate_rsa_prime(30)
    print "Jacobi(1001,9907): ", jacobi(1001, 9907), " jacobi(19,45): ", jacobi(
        19, 45), " jacobi(3,15)  ", jacobi(3, 15)
