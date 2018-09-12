#!/usr/bin/python
#-*- coding: utf-8 -*-

import socket
import struct
import binascii
import array
import sys
import numpy as np
from bitstring import BitArray
try:
    from astropy.time import Time as at
    astropy=True
except ImportError:
    astropy=False
    print("""WARNING: Cannot import astropy.time. Will therefore skip 
    automatic conversion of timestamps to ISO format.  Modified Julian Date
    (MJD) and MJD in seconds (mjds) will still be available in dictionaries.""")

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
    coordcode = h2s(h,i+4)
    coordsys = coordcode_to_name(coordcode)
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

def bin_swap_hex(binary):
    """ Input: binary sequence, assuming 4-byte items.
    Output: hexadecimal representation of the byte-swapped 
    (little/big endian) binary"""
    # Assume each item is 4-bytes, so number of items to swap is len(rawmsg)/4
    nb = int(len(binary)*0.25)
    # swap byte order
    msg = struct.pack('<'+str(nb)+'i', *struct.unpack('>'+str(nb)+'i', binary))
    # convert msg to hexadecimal version for convenience
    hexmsg = binascii.hexlify(msg)
    return hexmsg

def parse_status_message(b,h):
    stm = {}
    stm['binary_message_length'] = len(b)
    # We know we're parsing a status message.  Start extracting various
    # intersting bits according to Table 4.50 in HSL2 documentation
    stm['telnumber'] = h2i(h, 16) # Telescope ID number as integer
    stm['telname'] = b2c(b, 17).replace("\x00","") # Telescope ID name
    stm['msgflags'] = h2s(h, 25)[-4:] # Message and parking flags
    # Check if the "No real data", Table 4.51, flag is set. If so, skip status
    if not stm['msgflags'][-1]=='2':
        stm['status'] = parse_telstatus(b,h) # telescope status Table 4.52
    else:
        stm['status'] = None
    return stm

def parse_binary(b):
    # To parse the binary data, we use both the raw binary and also a 
    # byte-swapped (big/little) endian revsion for simpler extraction and
    # comparison of hexadecimal strings. 
    h = bin_swap_hex(b)
    # The raw binary is used to extract
    # e.g. double precision numbers and long char strings which are not
    # byte-flipped the way the rest of the data are.

    # We only want to process Telescope Status Action Status messages, 
    # as described in the document HSL2 Message Formats, version 2.29, 
    # Section 4.4.21 Telescope Status. We parse the fields defined 
    # in table Table 4.50.

    # There are many messages going around of different kinds, in addition to 
    # the status messages that we want. To select the ones we want, we 
    # use some values early in the hexadecimal sequence:
    messagetype = h2s(h, 1)
    actioncode = h2s(h, 13)
    actionstatus = h2s(h, 14)
    commandcode = h2s(h, 15)
    telnumber = h2s(h, 16)

    if (messagetype == "00000100" and actioncode == "00070800"
        and actionstatus == "08800001" and commandcode == "00000000"
        and telnumber != "ffffffff"):
        # Yes, we have the right message receied!
        # Parse message, extracting useful things
        return parse_status_message(b,h)

def allocation_to_name(hexall):
    """Input: String with allocation code
       Output: String with symbolic name from Table 4.20"""
    code = hexall.strip('0')
    names={}
    names['0'] = 'not_in_config'
    names['1'] = 'control'
    names['2'] = 'non_control'
    names['3'] = 'deallocate'
    return names[code]

def control_to_name(code):
    """Input: String with control code
       Output: String with symbolic name from Table 4.21"""
    names={}
    names['00000000'] = 'Manual'
    names['00000001'] = 'Local'
    names['00000002'] = 'Control_Room'
    names['00000003'] = 'Merlin'
    # Code 4 not defined in Table 4.21
    names['00000005'] = 'VLBI'
    names['00000006'] = 'Observing_room'
    names['00000007'] = 'eMerlin'
    names['00000008'] = 'Test'
    return names[code]

def coordcode_to_name(coordhex):
    """ Input: String with coordinate system code
        Output: String with coordinate system name from Table 4.12
    """
    names = {}
    names["00000000"] = "Invalid"
    names["00000001"] = "Az/El"
    names["00000002"] = "Ra/Dec Date"
    names["00000003"] = "B1950"
    names["00000004"] = "Galactic"
    names["fffffffd"] = "J2000"
    # Ensure lower-case comparison to get J2000 right
    csys = names[coordhex.lower()]
    return csys

def parse_telstatus(b,h):
    telstatus = {}
    telstatus['time_mjds'] = b2d(b, 26)# Time stamp [MJD in seconds]
    # For convenience, also convert directly to MJD
    telstatus['time_mjd'] = telstatus['time_mjds']/(24*3600.0)# Time stamp [MJD]
    # and to ISO 8601 compliant date-time format “YYYY-MM-DDTHH:MM:SS.sss…”
    if astropy:
        telstatus['time_isot'] = at(telstatus['time_mjd'], format='mjd').isot
    telstatus['jobnum'] = h2s(h, 28) # Job ID number
    telstatus['jobname'] = b2c(b, 29).replace("\x00","") # Job ID name
    telstatus['allocation'] = allocation_to_name(h2s(h, 37)) # Allocation-symbol
    telstatus['control'] = control_to_name(h2s(h, 38)) # Controller-symbol
    # Statusflags 
    telstatus['statusflags1'] = BitArray(hex=h2s(h, 39)).bin # See table 4.53
    if telstatus['statusflags1'][-2]:
        telstatus['azmotor'] = True
    else:
        telstatus['azmotor'] = False
    if telstatus['statusflags1'][-3]:
        telstatus['elmotor'] = True
    else:
        telstatus['elmotor'] = False
    telstatus['statusflags2'] = h2s(h, 40) # See table 4.54
    telstatus['statusflags3'] = h2s(h, 41) # See table 4.55
    # Read position parts of message:
    telstatus['actual_azel'] = readpos(b, h, 42) # Actual az/el
    telstatus['demanded_azel'] = readpos(b, h, 57) # Demanded az/el
    telstatus['demanded_lonlat'] = readpos(b, h, 72) # Demanded Long/Lat (RA/Dec)
    telstatus['offsets_azel'] = readoff(b, h) # Read az/el offsets
    telstatus['source'] = readsource(b, h) # Source data, name etc.
    telstatus['exp'] = readexp(b, h) # Exp data, exp ID
    return telstatus

def parse_receivers(b,h):
    recstat = {}
    # receiver statuses header
    recstat['numrec'] = h2i(h, 125)
    recstat['numactiverec'] = h2i(h, 126)
    recstat['active_recs'] = {}
    recstat['active_recs']['carouselpos'] = h2i(h, 127)
    recstat['active_recs']['carouselang'] = h2i(h, 128)
    recstat['active_recs']['recnumloc'] = h2i(h, 130)
   
    # Read receiver statuses for this telescope message
    recstat['recstatuses'] = []
    # Recoffset acumulates the length of all the receiver info for this telescope
    recoffset = 0
    currentrec = ""
    for recn in range(numrec):
        rec = readrec(b,h,131+offset)
        recstat['recstatuses'].append(rec)
        # Each receiver entry is 63 bytes of static info plus 18 bytes per LO entry
        offset += 63 + rec["numlo"] * 18
        if rec["carpos"]==acrec["carpos"]:
            currentrec = rec["idname"]
    recstat['currentrec'] = currentrec
   
    # There are two Receiver IF and Noise Diode Data entries for each
    # currently active receiver (one for each receiver channel). Table
    # 4.59 shows the format for a single entry.
    # start reading at byte after receiver info
    stb= 131 + offset
    ifoff = 0
    recstat['ifnoiseentries'] = []
    for recn in range(numrec*2):
        recstat['ifnoiseentries'].append(readIFnoise(b, h, stb))
        ifoff += 10
    # The length of the receier section varies, so return also the lastbyte
    # to enable further parsing of the following sections
    lastbyte = stb+ioff
    return recstat, lastbyte

def parse_noise_diode_status(b,h):
    """Parse data according to table 4.60
    """
    if ("" in telname):# or ("Mark" in telname):
        #print repr(h)
        #noisestatus = readnoisestatus(b, h, stb + ifoff)
        ifoff += 10
        st = stb + ifoff

    #receiverstatus, lastrecbyte = parse_receivers(b,h) # receiver statuses
    # TODO: Noisediode parsing fails for some telescopes,
    #       may be due to incomplete reciver info so wrong byte counter
    #noisediode = parse_noise_diode_status(b,h,lastrecbyte+1)
    # PARSE ALL REMAINING DATA UNTIL MET-data
        # Table 4.4.21.11 Met Status starts att byte 711 for Mk2...
        # But apparently only for Mk2. Need to figure out how to 
        # understand which is the right way to find this for other tels
        #mb = 711
        #metmjds = struct.unpack('d', rawmsg[4*(mb):4*(mb+2)])[0] # MJD in seconds
        #metwind = struct.unpack('d', rawmsg[4*(mb+2):4*(mb+4)])[0]
        #metwindmean = struct.unpack('d', rawmsg[4*(mb+4):4*(mb+6)])[0]
        #metwindpeak = struct.unpack('d', rawmsg[4*(mb+6):4*(mb+8)])[0]
        #metwinddir = struct.unpack('d', rawmsg[4*(mb+8):4*(mb+10)])[0]
        #metwindmeandir = struct.unpack('d', rawmsg[4*(mb+10):4*(mb+12)])[0]
        #metrain = struct.unpack('d', rawmsg[4*(mb+12):4*(mb+14)])[0]
        #metdrytemp = struct.unpack('d', rawmsg[4*(mb+14):4*(mb+16)])[0]

def print_teldata(td):
    if td['status']:
        toprint = td['status']['time_isot'], td['telname'], td['telnumber'], td['status']['actual_azel'][0:2], td['status']['demanded_azel'][0:2]
    else:
        toprint = td['telname'], td['telnumber'], 'NOSTATUS'
    print(toprint)

def joinMcast(mcast_addr,port,if_ip):
    """
    Returns a live multicast socket
    mcast_addr is a dotted string format of the multicast group
    port is an integer of the UDP port you want to receive
    if_ip is a dotted string format of the interface you will use
    """
    
    print("""Will attempt to listen to multicast assuming, this computer has a
            network interface with the 192-network IP """ + iface_ip + """. If no
            data, change iface_ip variable to right IP for this computer.""")

    #create a UDP socket
    mcastsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    #allow other sockets to bind this port too
    mcastsock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    #explicitly join the multicast group on the interface specified
    mcastsock.setsockopt(socket.SOL_IP,socket.IP_ADD_MEMBERSHIP,
                socket.inet_aton(mcast_addr)+socket.inet_aton(if_ip))

    #finally bind the socket to start getting data into your socket
    mcastsock.bind((mcast_addr,port))

    return mcastsock

if __name__ == "__main__":
    print("Running hsl2lib standalone, will parse binary stream...")
    # If DEBUG, allow exceptions to stop code. If False, catch exceptions and only print ERROR: line.
    DEBUG = False
    
    # Configuration
    mcast_port  = 7022
    mcast_group = "239.0.0.254"
    iface_ip    = "192.168.101.10" # Assume this computer has this 192-address
    
    # Connect to socket
    msock = joinMcast(mcast_group, mcast_port, iface_ip)
    
    while True:
        # Create empty dictionary to store telescope status data
        teldata = {}
        # Read data as raw binary message
        binary = msock.recv(4096)
        # If data starts with known "magic number" eMRL (but backwards due to
        # little/big endian byteflip)...
        if binary[0:4]=="LRMe":
            # then parse the binary into a dictionary of telescope information for
            # this telescope 
            if DEBUG:
                teldatum = parse_binary(binary)
            else:
                try: 
                    teldatum = parse_binary(binary)
                except:
                    teldatum = None
                    print("ERROR: Failed to read HSL2 binary ", binary)
                if teldatum:
                    teldata[teldatum['telname']] = teldatum
                    #print_teldata(teldatum)
                    if "Mark" in teldatum['telname']:
                    #if "Pick" in teldatum['telname']:
                        print teldatum
    msock.close()
