#!/usr/bin/python
#-*- coding: utf-8 -*-
import select, socket, sys, Queue
import sys, os
import json
import numpy as np
# Add script directory to include path
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from hsl2lib import *

def print_teldata(td):
    if td['status']:
        arec = td['status']['receiverstatus']['currentrec']
        act = np.array(td['status']['actual_azel'][0:2])*180/np.pi
        dem = np.array(td['status']['demanded_azel'][0:2])*180/np.pi
        toprint = td['status']['time_isot'], "Binary length", td['binary_message_length'], td['telname'], td['status']['control'], "Az ", act[0], " dem ", dem[0], " El ", act[1], " dem ", dem[1],"Receiver: ", arec
    else:
        toprint = td['telname'], td['telnumber'], 'NOSTATUS'
    print(toprint)


# Inspired by https://steelkiwi.com/blog/working-tcp-sockets/
print("Starting HSL2 receiver socket server, listening to multicast data and client requests...")
# If DEBUG, allow exceptions to stop code. If False, catch exceptions and
# only print ERROR: line.
DEBUG = False

# Multicast configuration
mcast_port  = 7022
mcast_group = "239.0.0.254"
iface_ip    = "192.168.101.10" # Assume this computer has this 192-address
# Connect to multicast
msock = joinMcast(mcast_group, mcast_port, iface_ip)
msock.setblocking(0)

# Server config, waiting for clients to request data (as a dictionary sent via socket)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind(('localhost', 50000)) # Only listen to localhost
server.listen(5) # Accept up to 5 local connections
inputs = [server, msock]
outputs = []
message_queues = {}

# Create empty dictionary to store telescope status data
teldata = {}
while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    for s in readable:
        if s is server:
            connection, client_address = s.accept()
            connection.setblocking(0)
            inputs.append(connection)
            message_queues[connection] = Queue.Queue()
        elif s is msock:
            # Read data
            binary = s.recv(4096)
            # If in python3, then this is a bytestring and we convert to string
            if (sys.version_info > (3, 0)):
                magicno = binary[0:4].decode()
            else:
                magicno = binary[0:4]
            # If data starts with known "magic number" eMRL (but backwards due to
            # little/big endian byteflip)...
            if magicno=="LRMe":
                # ... then parse the binary into a dictionary of telescope
                # information for this telescope 
                if DEBUG:
                    teldatum = parse_binary(binary)
                else:
                    try: 
                        teldatum = parse_binary(binary)
                    except Exception as e:
                        teldatum = None
                        print("ERROR: Failed to read HSL2 binary ", binary)
                        print("       Exception:", e)
                if teldatum:
                    print("SUCCESS: Received", teldatum['binary_message_length'], "bytes of HSL2 data for", teldatum['telname'])
                    teldata[teldatum['telname']] = teldatum
        else:
            try:
                request = s.recv(1024)
            except:
                print("ERROR communicating with client.")
            if request:
                message_queues[s].put(request)
                if s not in outputs:
                    outputs.append(s)
            else:
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()
                del message_queues[s]

    for s in writable:
        try:
            try:
                next_msg = message_queues[s].get_nowait()
            except Queue.Empty:
                outputs.remove(s)
            else:
                if next_msg == "TELDATA?":
                    telstring = json.dumps(teldata)
                    s.send(telstring)
                else:
                    s.send("IGNORED")
        except:
            print("ERROR communicating with client.")

    for s in exceptional:
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        del message_queues[s]
