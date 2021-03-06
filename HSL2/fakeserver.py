#!/usr/bin/python
#-*- coding: utf-8 -*-
import sys, os
import json
import numpy as np
import datetime
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
iface_ip    = "192.168.101.99" # Assume this computer has this 192-address
# Connect to multicast
#msock = joinMcast(mcast_group, mcast_port, iface_ip)
#msock.setblocking(0)

# Server config, waiting for clients to request data (as a dictionary sent via socket)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind(('localhost', 50000)) # Only listen to localhost
server.listen(5) # Accept up to 5 local connections
inputs = [server]
outputs = []
message_queues = {}

with open('./data.json') as f:
    teldata = json.load(f)

print(teldata.keys())

# Create empty dictionary to store telescope status data
while inputs:
    print("new loop")
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    for s in readable:
        if s is server:
            connection, client_address = s.accept()
            connection.setblocking(0)
            inputs.append(connection)
            print("Client connected...")
            message_queues[connection] = queue.Queue()
        #elif s is msock:
        #    # Read data
        #    binary = s.recv(4096)
        #    # If in python3, then this is a bytestring and we convert to string
        #    if (sys.version_info > (3, 0)):
        #        magicno = binary[0:4].decode()
        #    else:
        #        magicno = binary[0:4]
        #    # If data starts with known "magic number" eMRL (but backwards due to
        #    # little/big endian byteflip)...
        #    if magicno=="LRMe":
        #        # ... then parse the binary into a dictionary of telescope
        #        # information for this telescope 
        #        try: 
        #            teldatum = parse_binary(binary)
        #            if teldatum:
        #                teldata[teldatum['telname']] = teldatum
        #                utcnow = datetime.datetime.utcnow().isoformat()
        #                print("{0} UTC: Received {1} bytes of HSL2 data for {2}".format(utcnow, teldatum['binary_message_length'], teldatum['telname']))
        #        except Exception as e:
        #            print("ERROR: Failed to read HSL2 binary ", binary)
        #            print("       Exception:", e)
        #            print("       Assuming nothing to worry about, and continuing...")
        else:
            # Read client request...
            try:
                request = s.recv(1024)
                print("Got request", request)
                if request =="":
                    request = None
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
                if next_msg == "ALL":
                    telstring = json.dumps(teldata)
                    reply = telstring
                elif next_msg in teldata.keys():
                    telstring = json.dumps(teldata[next_msg])
                    reply = telstring
                else:
                    reply = "IGNORED"
                reply = str(len(reply)) + reply
                # If python 3 (and not python 2), then encode
                if (sys.version_info > (3, 0)):
                    reply = reply.encode()
                s.send(reply)
                print("Sent message", reply)
            except queue.Empty:
                pass
                #outputs.remove(s)
        except:
            print("ERROR writing to client.")

    for s in exceptional:
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        del message_queues[s]
    print(len(outputs))
