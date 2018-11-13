#!/usr/bin/python
#-*- coding: utf-8 -*-
# NOTE: Simple client to request HSL2 dictionaries from a receiver server
#       application which is parsing the binary multicast
import json
import socket
import errno
import sys
import numpy as np

def print_teldata(td):
    if td['status']:
        arec = td['status']['receiverstatus']['currentrec']
        act = np.array(td['status']['actual_azel'][0:2])*180/np.pi
        dem = np.array(td['status']['demanded_azel'][0:2])*180/np.pi
        toprint = td['status']['time_isot'], "Binary length", td['binary_message_length'], td['telname'], "Control", td['status']['control'], "Az ", act[0], " dem ", dem[0], " El ", act[1], " dem ", dem[1],"Receiver: ", arec
    else:
        toprint = td['telname'], td['telnumber'], 'NOSTATUS'
    print(toprint)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('localhost', 50000))
    #s.connect(('130.88.9.212', 50000))
except socket.error as serr:
    if serr.errno != errno.ECONNREFUSED:
        # Not the error we are looking for, re-raise
        raise serr
    else:
        print("ERROR: Cannot connect to HSL2 server, is it not running?")
        sys.exit(1)

# Define string to send to get data
msg = 'Mark 2' # for single telescope, e.g. 'Mark 2'
# If in python3, use bytestring
if (sys.version_info > (3, 0)):
    msg = msg.encode()

s.sendall(msg)
# The answer will be a string starting with BEG, and ending with END.
# The data in between can be loaded as a json dictionary of telescope info
parts = ""
while True:
    part = s.recv(4096)
    # If in python3, decode from bytestring
    if (sys.version_info > (3, 0)):
        part = part.decode()
    if part[0:3]=="BEG":
        parts = part
    else :
        parts += part
    if part[-3:]=="END":
        break
teldata = json.loads(parts[3:-3])
print_teldata(teldata)
s.close()
