#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : get_max.py
# Author            : Swathi S Bhat
# Date              : 13.12.2018
# Last Modified Date: 13.12.2018
# Last Modified By  : Swathi S Bhat
from __future__ import print_function

from termcolor import colored
import random
from halo import Halo

def get_max(results, N):
    n = (N*(N-1))/2
    pairs = []
    for i in range(0,N-1):
        for j in range(i+1, N):
            pairs.append([i,j])

    lesser = []
    max_num = []

    for i in range(0,n):
        if results[i] == 1 and pairs[i][0] not in lesser:
            if pairs[i][0] not in max_num:
                max_num.append(pairs[i][0])
            if pairs[i][1] not in lesser:
                lesser.append(pairs[i][1])
        elif results[i] == 1 and pairs[i][0] in lesser:
            if pairs[i][1] not in lesser:
                lesser.append(pairs[i][1])
        elif results[i] == 0 and pairs[i][1] not in lesser:
            if pairs[i][1] not in max_num:
                max_num.append(pairs[i][1])
            if pairs[i][0] not in lesser:
                lesser.append(pairs[i][0])
        elif results[i] == 0 and pairs[i][1] in lesser:
            if pairs[i][0] not in lesser:
                lesser.append(pairs[i][0])
        """
        print("pairs: [{}, {}]".format(pairs[i][0], pairs[i][1]))
        print("max_num: ",max_num)
        print("lesser: ",lesser)
        print("-----------------")
        """

    winner = [i for i in list(set(max_num)^set(lesser)) if i in max_num]
    print("-----------------")
    if len(winner) > 1:
        spinner = Halo(text="Error - winner list length > 1",spinner="dots")
        spinner.start()
        spinner.fail()
        #print("Error - winner list length > 1")
    print(colored("Winner: Bidder {}","white").format(winner[0]+1))

if __name__ == "__main__":

    N = int(raw_input("Enter number of inputs: "))
    results = [random.randint(0,1) for i in range(0,n)]
    print("Results: ",results)
    get_max(results, N)


