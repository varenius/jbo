#!/usr/bin/env python
#-*- coding: utf-8 -*-

import telnetlib
import sys
import os

timeout = 1 # seconds to wait for comms
# IPs of the telescopes
addr = {'lovell': '192.168.101.23', 
        'mark2':  '192.168.101.24'}
port=23 #Standard telnet port 23
# FS file containing the currently selected telescope; JB-MK2 or JB-LVL
telfile = "/usr2/control/location.ctl"

arg = sys.argv[1] # check or switch

def get_fs_tel():
    # get station name from file, assuming there is 
    # ONE line like "JB-MK2         Station Name"
    # with  either JB-MK2 or JB-LVL
    tsel = ""
    for line in open(telfile):
        if "Station Name" in line:
            tsel = line.split()[0]
        break
    return tsel 

def fslog(msg):
    # Append message to the FS system log
    cmd2 = "inject_snap \""+msg.replace(" ","\\ "))
    os.system(cmd)

if arg=="check":
    # Check current status of the cal switches
    for t in addr.keys():
        try: 
            tn = telnetlib.Telnet(addr[t], port, timeout)
            tn.read_until("\r\n", timeout)
            tn.write("SWPORT?\n")
            res = tn.read_some()
            if res.strip()=="0":
                fslog("STATUS: calswitch for {0} set to VLBI".format(t))
            elif res.strip()=="1":
                fslog("STATUS: calswitch for {0} set to PULSARS".format(t))
            else:
                fslog("ERROR: calswitch status command failed for {0} at {1}.".format(t, addr[t]))
        except: 
            fslog("ERROR: Failed to communicate with {0} calswitch at {1}".format(t,addr[t]))
            sys.exit()

elif arg=="switch":
    try: 
        # get current FS telescope, JB-MK2 or JB-LVL
        ctel = get_fs_tel()
        # enable VLBI cal for ctel, disable for the other tel
        if ctel =="JB-MK2":
            enable = "mark2"
            disable = "lovell"
        elif ctel =="JB-LVL":
            enable = "lovell"
            disable = "mark2"
        # enable cal
        tn1 = telnetlib.Telnet(addr[enable], port, timeout)
        tn1.read_until("\r\n", timeout)
        tn1.write("SETA=0\n") # Channel A, VLBI
        res1 = tn1.read_some()
        if res1.strip()=="1":
            fslog("SUCCESS: calswitch for {0} set to VLBI".format(enable))
        else:
            fslog("ERROR: Input select command failed for {0} calswitch at {1}.".format(enable,addr[enable]))
        # disable cal
        tn2 = telnetlib.Telnet(addr[disable], port, timeout)
        tn2.read_until("\r\n", timeout)
        tn2.write("SETA=1\n") # Channel B, PULSARS
        res2 = tn2.read_some()
        if res2.strip()=="1":
            fslog("SUCCESS: calswitch for {0} set to PULSARS".format(disable))
        else:
            fslog("ERROR: Input select command failed for {0} calswitch at {1}.".format(disable,addr[disable]))
    except: 
        fslog("ERROR: Failed to communicate with calswitch. Check connection?")
