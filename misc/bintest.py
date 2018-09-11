#!/usr/bin/python
#-*- coding: utf-8 -*-

from socket import *
import struct
import binascii
import datetime
import array
import sys
import numpy as np

# Specify 192-network IP of the machine running this script
# This is used to find the network interface to use for listening
# to the multicast from OTCX (on 192.168.101.3)
interface_ip    = "192.168.101.10"
# Set multicast port and group for HSL2 messages from OTCX
multicast_port  = 7022
multicast_group = "239.0.0.254"

# Connect to OTCX
s = socket(AF_INET, SOCK_DGRAM )
s.bind(("", multicast_port ))
mreq = inet_aton(multicast_group) + inet_aton(interface_ip)
s.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, str(mreq))
    
# Coordinate systems lookup Table 4.12
coorddict = {}
coorddict["00000000"] = "Invalid"
coorddict["00000001"] = "Az/El"
coorddict["00000002"] = "Ra/Dec Date"
coorddict["00000003"] = "B1950"
coorddict["00000004"] = "Galactic"
coorddict["fffffffd"] = "J2000"

def b2c(b, i):
    """ Slice 4*8=32 bytes out of binary sequence corresponding
        to a char, starting  at position i, and return as string. """
    return b[4*i:4*(i+8)]

def b2s(b, i):
    """ Slice 4 bytes out of binary sequence, starting
        at position i, and return as string. """
    return b[4*i:4*(i+1)]

def h2i(h, i):
    """ Slice 4 bytes out of hexadecimal string, starting
        at position i, and return as integer. """
    return int(h[8*i:8*(i+1)])

def h2s(h, i):
    """ Slice 4 bytes out of hexadecimal string, starting
        at position i, and return as string. """
    return h[8*i:8*(i+1)]

def b2d(b, i):
    """ Slice 8 bytes out of binary sequence, starting
        at position i, and return as double. """
    return struct.unpack('d', b[4*i:4*(i+2)])[0]

def readpos(b, h, i):
    """ Reads a position segment of data as defined in Table 4.52.
        This is used for convenience since the actual, demanded az/el and lon/lat 
        all three have the same format. Uses binary for decimal values and hex for 
        coordsys."""
    coord1 = b2d(b,i)
    coord2 = b2d(b,i+2)
    coordsys = h2s(h,i+4)
    parallax = b2d(b,i+5)
    rate1 = b2d(b,i+7)
    rate2 = b2d(b,i+9)
    radvel = b2d(b,i+11)
    date = b2d(b,i+13)
    return [coord1, coord2, coordsys, parallax, rate1, rate2, radvel, date]

def readoff(b, h):
    """ Reads a offset segment of data as defined in Table 4.52.
        Uses binary for decimal values and hex sec-codes."""
    i = 87
    azoff = b2d(b,i)
    eloff = b2d(b,i+2)
    sec = h2s(h, i+4)
    azoffrate = b2d(b,i+5)
    eloffrate = b2d(b,i+7)
    ratesec = h2s(h, i+9)
    return [azoff, eloff, sec, azoffrate, eloffrate, ratesec]

def readsource(b, h):
    sourceid = h2s(h, 97)
    sourceidname = b2c(b, 98).replace("\x00","") # 8x4=32 byte char
    sourcealtname = b2c(b, 115).replace("\x00","") # 8x4=32 byte char
    return sourceid, sourceidname, sourcealtname
         
def readexp(b, h):
    expid = h2s(h, 106)
    expidname = b2c(b,107).replace("\x00","") # 8x4=32 byte char
    return expid, expidname
         
def readLO(b,h,i):
    lo = {}
    lo["loidnum"] = h2i(h,i)
    lo["loidname"] = b2c(b,i+1).replace("\x00","")
    lo["loidfreq"] = b2d(b,i+9)
    return lo
             
def readrec(b, h, i):
    # Each receiver entry has a length of
    # "header", idnum to numlo = 22 bytes
    # LO entries = numlo*18 bytes
    # receiver info 40 bytes
    #  so offset index to next receiver is = 62+numlo*18 + 1
    rec = {}
    rec["idnum"] = h2i(h,i)
    rec["idname"] = b2c(b,i+1).replace("\x00","")
    rec["carpos"] = h2i(h,i+9)
    rec["carang"] = b2d(b,i+10)
    rec["numincar"] = h2i(h,i+12)
    rec["freqidnum"] = h2s(h,i+13)
    rec["freqidname"] = b2c(b,i+14).replace("\x00","")
    rec["numlo"] = h2i(h,i+22)
    for k in range(rec["numlo"]):
        # read each LO
        offset = k*18 # each LO table is 18 bytes
        rec["lo"+str(k)] = readLO(b,h,i+23+offset)
    return rec

def readIFnoise(b,h,i):
    # Each entry is 11 bytes
    ifnoise = {}
    ifnoise["auto"] = h2i(h,i)
    ifnoise["timeconst"] = h2i(h,i+1)
    ifnoise["meanpower"] = h2i(h,i+2)
    ifnoise["rms"] = h2i(h,i+3)
    ifnoise["nsamp"] = h2i(h,i+4)
    ifnoise["normnoisediode"] = h2i(h,i+5)
    ifnoise["timeconstmean"] = h2i(h,i+6)
    ifnoise["offpow"] = h2i(h,i+7)
    ifnoise["onpow"] = h2i(h,i+8)
    ifnoise["dectzero"] = h2i(h,i+9)
    ifnoise["iflevel"] = h2i(h,i+10)
    return ifnoise

def readnoisestatus(b,h,i):
    # Each entry is 10 bytes
    noise = {}
    noise["timestamp"] = b2d(b,i)
    noise["enabled"] = h2i(h,i+2)
    noise["period"] = b2d(b,i+3)
    noise["duty"] = b2d(b,i+5)
    noise["phase"] = b2d(b,i+7)
    noise["autocal"] = h2i(h,i+9)
    noise["totpow"] = h2i(h,i+10)
    return noise

# receive and parse multicast messages
# in binary format
while True:
    # Read data as raw binary message
    rm = s.recv(4096)
    # Check if sane data
    if rm[0:4]=="LRMe":
        # If data starts with known token,
        # i.e. the "magic number" eMRL - but backwards -
        # then create a byte-swapped (big/little) endian copy
        # to use to compare hexadecimal strings 
        # Assume each item is 4-bytes, so number of items to swap is len(rawmsg)/4
        b = int(len(rm)*0.25)
        # swap byte order
        msg = struct.pack('<'+str(b)+'i', *struct.unpack('>'+str(b)+'i', rm))
        # convert msg to hexadecimal version for convenience
        hm = binascii.hexlify(msg)
        hexmsg = hm
        rawmsg = rm
        # Extract hex-strings from header to check if we want to parse this message
        messagetype = h2s(hm, 1)
        actioncode = h2s(hm, 13)
        actionstatus = h2s(hm, 14)
        commandcode = h2s(hm, 15)
        telnumber = h2s(hm, 16)
        msgflags = h2s(hm, 17)

    # There are many messages going around of different kinds.
    # Only parse the telescope status broadcast messages, so filter
    # on a number of hex data fields
    if (
       # Telescope Status Action Status message, as described in
       # HSL2 Message Formats, version Version 2.29, Section
       # 4.4.21 Telescope Status, Table 4.50
       messagetype == "00000100"
       and actioncode == "00070800"
       and actionstatus == "08800001"
       and commandcode == "00000000"
       and telnumber != "ffffffff"):
         # Yes, we have the right message receied!
         # Parse message, extracting useful things
         # Some values are decoded wrong if using the byte-swapped data since
         # they are not simple 4-byte units. In those cases, use the raw binary
         telname = b2c(rm, 17) # Table 4.50
         jobname = b2c(rm, 29) # Table 4.50
         allocationstate = h2s(hm, 37) # See table 4.20
         controller = h2s(hm, 38) # See table 4.21

         # Read position parts of message:
         # Actual az/el
         act_azel = readpos(rm, hm, 42)
         # Demanded az/el
         dem_azel = readpos(rm, hm, 57)
         # Demanded RA/Dec
         dem_radec = readpos(rm, hm, 72)
         # Read Az/el offsets
         offsets = readoff(rm, hm)
         
         # Source data, name etc.
         source = readsource(rm, hm)
         # Exp data, exp ID etc.
         exp = readexp(rm, hm)

         # dummy telescope status

         # receiver statuses header
         numrec = h2i(hm, 125)
         numactiverec = h2i(hm, 126)

         # active receiver list
         acrec= {}
         acrec["carpos"] = h2i(hm, 127)
         acrec["carang"] = b2d(rm, 128)
         acrec["recnum"] = h2i(hm, 130)

         # Read receiver statuses for this telescope message
         recstatuses = []
         # Recoffset acumulates the length of all the receiver info for this telescope
         recoffset = 0
         currentrec = ""
         for recn in range(numrec):
             rec = readrec(rm,hm,131+recoffset)
             recstatuses.append(rec)
             # Each receiver entry is 63 bytes of static info plus 18 bytes per LO entry
             recoffset += 63 + recstatuses[-1]["numlo"] * 18
             if rec["carpos"]==acrec["carpos"]:
                 currentrec = rec["idname"]

         # There are two Receiver IF and Noise Diode Data entries for each
         # currently active receiver (one for each receiver channel). Table
         # 4.59 shows the format for a single entry.
         # start reading at byte after receiver info
         stb= 131 + recoffset
         ifoff = 0
         ifnoiseentries = []
         if ("Mark" in telname):
             print "tel, act, dem in radians", telname, act_azel[0:2], dem_azel[0:2]
         #if ("Pick" in telname) or ("Mark" in telname):
         #    for recn in range(numrec*2):
         #        ifnoiseentries.append(readIFnoise(rm, hm, stb))
         #        ifoff += 10
         #    #print(hm[8*(stb+ifoff):8*(stb+ifoff+36)])
         #    st = stb + ifoff-12
         #    print telname, len(rm), st, act_azel
         #    #noisestatus = readnoisestatus(rm, hm, stb + ifoff)
         #    #print noisestatus
         #    #print((rm))
         #    print rm[4*st:]
         #    print hm[8*st:]
         #    #print(repr(b2d(rm,st)))
         #    print(repr(h2s(hm,st)))

         #if "Mark" in telname:
         #if "" in telname:
         #    print telname, currentrec
         #    pass

         #print telname, len(msg)

         #if "Mark" in telname:
         #    pass
             # Table 4.4.21.11 Met Status starts att byte 711
             # But apparently only for Mk2. Need to figure out how to 
             # understand which is the right way to find this for other tels
             # Possibly because of variable length messages for other tels, e.g. and edfa receiver lists?
             #mb = 711
             #metmjds = struct.unpack('d', rawmsg[4*(mb):4*(mb+2)])[0] # MJD in seconds
             #metwind = struct.unpack('d', rawmsg[4*(mb+2):4*(mb+4)])[0]
             #metwindmean = struct.unpack('d', rawmsg[4*(mb+4):4*(mb+6)])[0]
             #metwindpeak = struct.unpack('d', rawmsg[4*(mb+6):4*(mb+8)])[0]
             #metwinddir = struct.unpack('d', rawmsg[4*(mb+8):4*(mb+10)])[0]
             #metwindmeandir = struct.unpack('d', rawmsg[4*(mb+10):4*(mb+12)])[0]
             #metrain = struct.unpack('d', rawmsg[4*(mb+12):4*(mb+14)])[0]
             #metdrytemp = struct.unpack('d', rawmsg[4*(mb+14):4*(mb+16)])[0]
             #print(telname)
             #print(metdrytemp)
         # DEBUG printing
             #st = 687 # Has MJD in seconds, not clear which
            # st = 711
            # print repr(rawmsg[st*4:])
            # print repr(hexmsg[st*8:])
            # for i in range(0,20,2):
            #     test = struct.unpack('d', rawmsg[4*(st+i):4*(st+i+2)])[0] # MJD in seconds
            #     print(i, repr(test))
            # test2 = struct.unpack('d', rawmsg[4*st:4*(st+2)])[0]
            # print(repr(test2))
             #print repr(hexmsg[165*8:200*8])
             #print repr(sourcealtname)
s.close()
