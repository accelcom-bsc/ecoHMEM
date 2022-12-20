#!/usr/bin/python

def text2bytes(text):
    if text[-1] >= '0' and text[-1] <= '9':
        text = text + 'b'
    mult = text[-1]
    size = float(text[:-1])
    if mult not in ("b", "B"):
        if mult in ("k", "K"):
            size *= 1024
        elif mult in ("m", "M"):
            size *= 1024**2
        elif mult in ("g", "G"):
            size *= 1024**3
        elif mult in ("t", "T"):
            size *= 1024**4
        else:
            print("Error in size modifier")
            sys.exit(1)
    return int(size)

