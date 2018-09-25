#!/usr/bin/python
#-*- coding: utf-8 -*-
import sys, os
import json
import numpy as np
import select, socket
# If python 3 (and not python 2), then import queue lowercase, else uppercase
if (sys.version_info > (3, 0)):
    import queue
else:
    import Queue as queue
# Add script directory to include path
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from hsl2lib import *

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
            message_queues[connection] = queue.Queue()
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
                # If python 3 (and not python 2), then decode
                if (sys.version_info > (3, 0)):
                    request = request.decode()
            except:
                print("ERROR reading from client.")
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
            except queue.Empty:
                outputs.remove(s)
            else:
                if next_msg == "TELDATA?":
                    telstring = json.dumps(teldata)
                    reply = telstring
                else:
                    reply = "IGNORED"
                # If python 3 (and not python 2), then encode
                if (sys.version_info > (3, 0)):
                    reply = reply.encode()
                s.send(reply)
        except:
            print("ERROR writing to client.")

    for s in exceptional:
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        del message_queues[s]
