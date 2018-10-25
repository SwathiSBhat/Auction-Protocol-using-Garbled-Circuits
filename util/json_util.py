from __future__ import print_function

import json 

# converts all unicode strings to string in json retrieved data
def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


if __name__ == "__main__":
    with open("../test/circuit.json",'r') as f:
        data = json.load(f)
    data = byteify(data)
    print(data)


