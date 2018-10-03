
def encode_str(m):
    """ 
    Encodes input tag to int in such a way that tag string
    can be recovered given the integer representation
    """
    s = ''.join(str(ord(x)).zfill(3) for x in m)
    return int(s)


def decode_str(a):
    """
    Decodes integer a to corresponding string 
    representing the tag 
    """
    s = str(a)
    if len(s)%3 != 0:
        quo = len(s)/3
        fill = (quo+1)*3 
        s = s.zfill(fill)
    a = [int(s[i:i+3]) for i in range(0,len(s),3)]
    a = [chr(x) for x in a]
    decoded_str = ''.join(x for x in a)
    return decoded_str

if __name__ == "__main__":
    s = raw_input("Enter string to encode: ")
    enc_s = encode_str(s)
    print "Encoded str: ",enc_s
    dec_s = decode_str(enc_s)
    print "Decoded str: ",dec_s 
