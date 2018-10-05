from __future__ import print_function

import json 
import jsonlines

def read_obj(filename):
    print("---------------ALL--------------------")
    with jsonlines.open(filename) as reader:
        for obj in reader:
            mycirc = obj
            print("------")
            print("Object: ",mycirc)
    print("--------------END OF ALL--------------")

def read_line(filename):
    indices = [2,3]
    count = 0
    with open(filename) as f:
        for i in range(0,len(indices)):
            line = f.readline()
            if count != indices[i]:
                while count != indices[i]:
                    line = f.readline()
                    count += 1
            data = json.loads(line)
            print("--------------")
            print("count: {} indices[{}] = {}".format(count,i,indices[i]))
            print("data: ",data)
        


if __name__ == "__main__":
    filename = "cut-and-choose.json"
    read_obj(filename)
    read_line(filename)

            
