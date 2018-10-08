#!/usr/bin/python
#-*- coding: utf-8 -*-
# NOTE: Simple client to request HSL2 dictionaries from a receiver server
#       application which is parsing the binary multicast
import json
import socket, select
import time
import numpy as np
import errno
import sys

def print_teldata(td):
    if td['status']:
        arec = td['status']['receiverstatus']['currentrec']
        act = np.array(td['status']['actual_azel'][0:2])*180/np.pi
        dem = np.array(td['status']['demanded_azel'][0:2])*180/np.pi
        toprint = td['status']['time_isot'], "Binary length", td['binary_message_length'], td['telname'], td['status']['control'], "Az ", act[0], " dem ", dem[0], " El ", act[1], " dem ", dem[1],"Receiver: ", arec
    else:
        toprint = td['telname'], td['telnumber'], 'NOSTATUS'
    print(toprint)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    #s.connect(('localhost', 50000))
    #s.connect(('127.0.0.1', 50000))
    s.connect(('130.88.9.212', 50000))
except socket.error as serr:
    if serr.errno != errno.ECONNREFUSED:
        # Not the error we are looking for, re-raise
        raise serr
    else:
        print("ERROR: Cannot connect to HSL2 server, is it not running?")
        sys.exit(1)

# Define string to send to get data
#msg = 'ALL'
msg = 'Mark 2'
# If in python3, use bytestring
if (sys.version_info > (3, 0)):
    msg = msg.encode()

while True:
    s.sendall(msg)
    data = s.recv(65536)
    # If in python3, decode from bytestring
    if (sys.version_info > (3, 0)):
        data = data.decode()
    teldata = json.loads(data)
    #with open('data.json', 'w') as outfile:
    #    json.dump(teldata, outfile, sort_keys=True, indent=4)
    #print_teldata(teldata['Mark 2'])
    print(teldata)
    sys.exit()
    time.sleep(1)
s.close()
