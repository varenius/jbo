#!/usr/bin/python
#-*- coding: utf-8 -*-
# NOTE: Simple client to request HSL2 dictionaries from a receiver server
#       application which is parsing the binary multicast
import json
import socket
import errno
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    #s.connect(('localhost', 50000))
    s.connect(('130.88.9.212', 50000))
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
data = s.recv(65536)
# If in python3, decode from bytestring
if (sys.version_info > (3, 0)):
    data = data.decode()
teldata = json.loads(data)
print(teldata)
s.close()
