#!/usr/bin/python
#-*- coding: utf-8 -*-
# NOTE: Special modules required: bitarray (to read HSL2 bit codes), netifaces
#       (to find out 192-IP of this computer), astropy (to convert time formats)
# NOTE: Many fields have MJDs, modified julian date in seconds. 
#       A value of -207360043201.0 in this field means 0 i.e. not set, since
#       -207360043201.0/(3600*24) = -2400000.5
import socket
import struct
import binascii
import datetime
import array
import sys
import numpy as np
from bitstring import BitArray
import netifaces as ni

try:
    from astropy.time import Time as at
    astropy=True
except ImportError:
    astropy=False
    print("""WARNING: Cannot import astropy.time. Will therefore skip 
    automatic conversion of timestamps to ISO format.  Modified Julian Date
    (MJD) and MJD in seconds (mjds) will still be available in dictionaries.""")

def get_192IP():
    """ Gets the 192.168.101.X IP of the current machine, assuming this is tied
    to the interface where we want to receiver the HSL2 multicast
    information."""
    for iface in ni.interfaces():
        ipv4addr = ni.ifaddresses(iface)[2][0]['addr']
        if '192.168.101.' in ipv4addr:
            return ipv4addr

def b2d(b, i):
    """ Slice 8 bytes out of binary sequence, starting
        at position i, and return as double. """
    return struct.unpack('d', b[4*i:4*(i+2)])[0]

def b2i(b, i):
    """ Slice 4 bytes out of binary sequence corresponding
        to a char, starting  at position i, and return as integer. """
    return struct.unpack('<i', b[4*i:4*(i+1)])[0]

def b2c128(b, i):
    """ Slice 4*32=128 bytes out of binary sequence corresponding
        to a char, starting  at position i, and return as string. """
    ans = b[4*i:4*(i+32)]
    # If python 3 (and not python 2), then decode string explicitly from bytestring
    if (sys.version_info > (3, 0)):
        ans = ans.decode()
    return ans

def b2c(b, i):
    """ Slice 4*8=32 bytes out of binary sequence corresponding
        to a char, starting  at position i, and return as string. """
    ans = b[4*i:4*(i+8)]
    # If python 3 (and not python 2), then decode string explicitly from bytestring
    if (sys.version_info > (3, 0)):
        ans = ans.decode()
    return ans

def h2i(h, i):
    """ Slice 4 bytes out of hexadecimal string, starting
        at position i, and return as integer. """
    return int(h2s(h,i))

def h2s(h, i):
    """ Slice 4 bytes out of hexadecimal string, starting
        at position i, and return as string. """
    return h[8*i:8*(i+1)]

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
    lo["loidnum"] = b2i(b,i)
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
    rec["idnum"] = b2i(b,i)
    rec["idname"] = b2c(b,i+1).replace("\x00","")
    rec["carpos"] = h2i(h,i+9)
    rec["carang"] = b2d(b,i+10)
    rec["numincar"] = b2i(b,i+12)
    rec["freqidnum"] = h2s(h,i+13)
    rec["freqidname"] = b2c(b,i+14).replace("\x00","")
    rec["numlo"] = h2i(h,i+22)
    nextbyte = i+23
    rec["LOs"] = []
    for k in range(rec["numlo"]):
        # read each LO
        lo = readLO(b,h,nextbyte)
        rec["LOs"].append(lo)
        nextbyte += 18 #each LO table is 18 bytes
    rec['frequency'] = b2d(b,nextbyte)
    rec['basebandfrequency'] = b2d(b,nextbyte+2)
    rec['azbeamsquint'] = b2d(b,nextbyte+4)
    rec['elbeamsquint'] = b2d(b,nextbyte+6)
    # ... focus etc.
    rec['cryotemp'] = b2d(b,nextbyte+30)
    rec['cryopressure'] = b2d(b,nextbyte+32)
    rec['compressorsupplypressure'] = b2d(b,nextbyte+34)
    rec['compressorreturnpressure'] = b2d(b,nextbyte+36)
    rec['heliumbottlepressure'] = b2d(b,nextbyte+38)
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

def parse_EDFA_status_block(b,h,i):
    """Parse data according to tables 4.66"""
    status = {}
    status["dest"] = h2s(h,i)
    status["number"] = h2s(h,i+1)
    status["mjds"] = b2d(b,i+2)
    status["numstagestatuses"] = h2i(h,i+4)
    status['stagestatuses']= []
    offset = 5
    #print("EDFASTATUS", status)
    #print(b2c(b,i+offset+2))
    for k in range(int(status['numstagestatuses'])):
        # Read EDFA status parameters for this stage from table 4.67
        status['stagestatuses'].append(read_467_EDFA_status(b,h,i+offset))
        offset += 25
    status["numpumpstatuses"] = h2i(h,i+4+offset)
    status['pumpstatuses']= []
    for k in range(int(status['numpumpstatuses'])):
        # Read pump status parameters for this stage from table 4.70
        status['pumpstatuses'].append(read_470_pump_status(b,h,i+offset))
        offset += 5
    # Read controller status, table 4.71
    status['controllersstatus'] = read_EDFA_controller_status(b,h,i+offset)
    offset +=49 # 49 bytes in controller status, table 4.71
    status['safetystatus'] = read_EDFA_safety_status(b,h,i+offset)
    offset +=9 # 9 bytes in safety status, table 4.74
    status['VOAsetting'] = b2d(b,i+offset)
    status['casetemp'] = b2d(b,i+offset+2)
    status['coiltemp'] = b2d(b,i+offset+4)
    status['heatertemp'] = b2d(b,i+offset+6)
    status['errors'], nextbyte = parse_errors(b,h,i+offset+8)
    return status, nextbyte

def read_EDFA_safety_status(b,h,i):
    # Table 4.74
    status = {}
    status['safetystatus'] = h2s(h,i)
    status['maximumsignal'] = b2d(b,i+1)
    status['minimumsignal'] = b2d(b,i+3)
    status['switchingtime'] = b2d(b,i+5)
    status['gain'] = b2d(b,i+7)
    return status

def read_EDFA_controller_status(b,h,i):
    # Table 4.71
    status = {}
    status['laserpower'] = h2s(h,i)
    status['PSUcurrent'] = b2d(b,i+1)
    status['PSUvoltage'] = b2d(b,i+3)
    status['PSUmode'] = h2s(h,i+5)
    status['PSUreason'] = b2c128(b,i+6).replace("\x00","") # read 32x4 bytes string
    status['firmwaremajorversion'] = h2s(h,i+38)
    status['firmwareminorversion'] = h2s(h,i+39)
    status['unitnumber'] = h2s(h,i+40)
    status['PSUvoltagelowerlim'] = b2d(b,i+41)
    status['PSUvoltageupperlim'] = b2d(b,i+43)
    status['PSUcurrentlowerlim'] = b2d(b,i+45)
    status['PSUcurrentupperlim'] = b2d(b,i+47)
    return status

def read_470_pump_status(b,h,i):
    # Table 4.70
    status = {}
    status['pumpnumber'] = h2s(h,i)
    status['pumptemp'] = b2d(b,i+1)
    status['pumpcurrent'] = b2d(b,i+3)
    return status

def read_467_EDFA_status(b,h,i):
    # Table 4.67
    status = {}
    status['stageidnumber'] = h2s(h,i)
    status['stageidname'] = b2c(b,i+1)
    status['powerin'] = b2d(b,i+9)
    status['totpowerout'] = b2d(b,i+11)
    status['sigpowerout'] = b2d(b,i+13)
    status['gain'] = b2d(b,i+15)
    status['targetpower'] = b2d(b,i+17)
    status['VOA'] = b2d(b,i+19)
    status['mode'] = h2s(h,i+21)
    status['options'] = h2s(h,i+22)
    status['power/gain'] = b2d(b,i+23)
    return status

def readtickbox(b,h,i):
    """Parse data according to tables 4.64, 4.65 """
    tickbox = {}
    tickbox["mjds"] = b2d(b,i)
    tickbox["status"] = BitArray(hex=h2s(h, i+2)).bin # See table 4.63
    tickbox["delay"] = b2d(b,i+3)
    tickbox["avg_delay"] = b2d(b,i+5)
    nextbyte = i + 7
    return tickbox, nextbyte

def readDINTstatus(b,h,i):
    """Parse data according to tables 4.61, 4.62, 4.53 """
    dint = {}
    dint["mjds"] = b2d(b,i)
    dint["adc8"] = {}
    dint["adc8"]["mjds"] = b2d(b,i+2)
    dint['adc8']["status"] = BitArray(hex=h2s(h, i+4)).bin # See table 4.63
    dint["adc8"]["tick_phase"] = b2d(b,i+5)
    dint["adc8"]["delay"] = b2d(b,i+7)
    dint["adc3"] = {}
    dint["adc3"]["mjds"] = b2d(b,i+9)
    dint['adc3']["status"] = BitArray(hex=h2s(h, i+11)).bin # See table 4.63
    dint["adc3"]["tick_phase"] = b2d(b,i+12)
    dint["adc3"]["delay"] = b2d(b,i+13)
    nextbyte = i+16
    return dint, nextbyte

def readnoisestatus(b,h,i):
    """Parse data according to table 4.60 """
    noise = {}
    noise["mjds"] = b2d(b,i)
    noise["enabled"] = h2s(h,i+2)
    noise["period"] = b2d(b,i+3)
    noise["duty"] = b2d(b,i+5)
    noise["phase"] = b2d(b,i+7)
    noise["autocal"] = h2i(h,i+9)
    noise["totpow"] = h2i(h,i+10)
    nextbyte = i + 11
    return noise, nextbyte

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
    #print(stm)
    # Check if the "No real data", Table 4.51, flag is set. If so, skip status
    if not stm['msgflags'][-1]=='2':
        stm['status'] = parse_telstatus(stm, b,h) # telescope status Table 4.52
    else:
        stm['status'] = None
    return stm

def parse_binary(b):
    # To parse the binary data, we use both the raw binary and also a 
    # byte-swapped (big/little) endian revsion for simpler extraction and
    # comparison of hexadecimal strings. 
    h = bin_swap_hex(b).decode()
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

def parse_telstatus(stm, b,h):
    # stm present for debug things, e.g. filter on telescopes
    tn = stm['telname']
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
    telstatus['receiverstatus'], nextbyte = parse_receivers(b,h) # receiver statuses
    # Next table should begin at nextbyte
    telstatus['noisediode_status'], nextbyte = readnoisestatus(b, h, nextbyte)
    telstatus['DINT_status'], nextbyte = readDINTstatus(b, h, nextbyte)
    telstatus['tickbox_status'], nextbyte = readtickbox(b, h, nextbyte)
    telstatus['EDFA_status'], nextbyte = parse_EDFA_status_block(b,h,nextbyte)
    # TODO: Find why this is needed
    nextbyte +=1
    pherstat, nextbyte = parse_pheripal_status(b,h,nextbyte)
    pstat, nextbyte = parse_phase_status(b,h,nextbyte)
    #print("p", pstat, nextbyte)
    lstat, nextbyte = parse_Lbandlink_status(b,h,nextbyte)
    #print("l", lstat, nextbyte)
    optstat, nextbyte = parse_optical_status(b,h,nextbyte)
    #print('o', optstat, nextbyte)
    metdata, nextbyte = parse_metdata(b,h,nextbyte)
    #print('m', metdata, nextbyte)
    sitestat, nextbyte = parse_sitestatus(b,h,nextbyte)
    #print('s',sitestat, nextbyte)
    #print("beforeerror",h[8*nextbyte:])
    #print("beforeerror",b[4*nextbyte:])
    errors, nextbyte = parse_errors(b,h,nextbyte)
    #print('e',errors, nextbyte)
    #print(tn, metdata['drytemp'], metdata['mjds'])
    return telstatus

def parse_pheripal_status(b,h,i):
    # Table 4.76
    status = {}
    status['mjds']= b2d(b,i)
    nextbyte = i+2
    return status, nextbyte

def parse_phase_status(b,h,i):
    # Table 4.77
    status = {}
    status['mjds']= b2d(b,i)
    status['LOsynthphase']= b2d(b,i+2)
    status['LOsynthamp']= b2d(b,i+4)
    status['cable_phase']= b2d(b,i+6)
    nextbyte = i+8
    return status, nextbyte

def parse_Lbandlink_status(b,h,i):
    # Table 4.78
    status = {}
    status['mjds']= b2d(b,i)
    status['smoothed_phase']= b2d(b,i+2)
    status['phase_slope']= b2d(b,i+4)
    status['phase_error']= b2d(b,i+6)
    status['phase_RMS_error']= b2d(b,i+8)
    status['phase']= b2d(b,i+10)
    status['link_state_count']= h2s(h, i+12)
    status['status'] = BitArray(hex=h2s(h, i+13)).bin # See Table 4.79
    # For some reason there an extra byte here, not described in table 4.78
    status['EXTRABYTE']= h2s(h, i+14)
    nextbyte = i+15
    return status, nextbyte

def parse_optical_status(b,h,i):
    # Table 4.80
    status = {}
    status['mjds']= b2d(b,i)
    status['numofEDFAstatuses']= b2i(b, i+2)
    status['EDFAstatuses'] = []
    offset = 3
    for k in range(int(status['numofEDFAstatuses'])):
        es = read_opt_EDFA_status(b,h,i+offset)
        status['EDFAstatuses'].append(es)
        offset += 13
    nextbyte = i+offset
    return status, nextbyte

def read_opt_EDFA_status(b,h,i):
    # Table 4.81
    status = {}
    status['repeateridnumber'] = h2s(h,i)
    status['repeateridname'] = b2c(b,i+1).replace("\x00","")
    status['EDFAdestination'] = h2s(h,i+9)
    status['EDFAnumber'] = h2s(h,i+10)
    status['EDFAinputstatus'] = h2s(h,i+11)
    status['EDFAoutputstatus'] = h2s(h,i+12)
    return status

def parse_sitestatus(b,h,i):
    sitestatus = {}
    sitestatus['mjds']= b2d(b,i)
    sitestatus['status']= BitArray(hex=h2s(h, i+2)).bin # unsigned long, 4 bytes i.e. 32 bits
    nextbyte = i+3
    return sitestatus, nextbyte
def parse_sitestatus(b,h,i):
    sitestatus = {}
    sitestatus['mjds']= b2d(b,i)
    sitestatus['status']= BitArray(hex=h2s(h, i+2)).bin # unsigned long, 4 bytes i.e. 32 bits
    nextbyte = i+3
    return sitestatus, nextbyte
def parse_sitestatus(b,h,i):
    sitestatus = {}
    sitestatus['mjds']= b2d(b,i)
    sitestatus['status']= BitArray(hex=h2s(h, i+2)).bin # unsigned long, 4 bytes i.e. 32 bits
    nextbyte = i+3
    return sitestatus, nextbyte

def parse_sitestatus(b,h,i):
    sitestatus = {}
    sitestatus['mjds']= b2d(b,i)
    sitestatus['status']= BitArray(hex=h2s(h, i+2)).bin # unsigned long, 4 bytes i.e. 32 bits
    nextbyte = i+3
    return sitestatus, nextbyte

def parse_errors(b,h,i):
    # 
    errors = {}
    errors['numerrors']= h2i(h,i)
    offset = 1
    errors['errorlist']=[]
    for k in range(errors['numerrors']):
        #print("PROCESSING ERROR:", h[8*(i+offset): 8*(i+offset+4)])
        error = {}
        error['code'] = h2s(h,i+offset)
        error['priority'] = h2s(h,i+offset+1)
        error['audible'] = h2s(h,i+offset+2)
        error['parameter'] = h2s(h,i+offset+3)
        errors['errorlist'].append(error)
        # Assume the parameter is always zero-value unsigned long...
        # From hsl2 document, 4.4.21.13:
        # The Parameter is a parameter associated with the error or warning. If
        # the error has no parameter it consists of a zero-value unsigned long.
        # Otherwise it is either an unsigned long, a double, or for string
        # parameters it is an unsigned long containing the transmitted length of
        # the string followed by the string itself. The string is always
        # transmitted as an even number of characters padded with a zero byte if
        # necessary.
        offset =+4
    nextbyte = i+offset
    #print('LAST', h[nextbyte*8:])
    #print('LAST', b[nextbyte*4:])
    return errors, nextbyte

def parse_receivers(b,h, i=123):
    recstat = {}
    # receiver statuses header
    recstat['mjds'] = b2d(b, i)
    recstat['numrec'] = h2i(h, i+2)
    recstat['numactiverec'] = h2i(h, i+3)
    recstat['active_recs'] = {}
    offset = 4
    for k in range(recstat['numactiverec']):
        recstat['active_recs']['carouselpos'] = h2i(h, i+offset)
        recstat['active_recs']['carouselang'] = b2d(b, i+offset+1)
        recstat['active_recs']['recnumloc'] = h2i(h, i+offset+3)
        offset +=4

    # read receiver statuses table
    recstat['recstatuses'] = []
    # store the current equipped receiver in currentrec variable for easy
    # access later
    recstat['currentrec'] = ""
    recstat['currentreccryotemp'] = ""
    for recn in range(recstat['numrec']):
        rec = readrec(b,h,i+offset)
        recstat['recstatuses'].append(rec)
        # Each receiver entry is 63 bytes of static info plus 18 bytes per LO entry
        offset += 63 + rec['numlo'] * 18
        if rec['carpos']==recstat['active_recs']['carouselpos']:
            recstat['currentrec'] = rec['idname']
            recstat['currentreccryotemp'] = rec['cryotemp']
   
    # There are two Receiver IF and Noise Diode Data entries for each
    # currently active receiver (one for each receiver channel). Table
    # 4.59 shows the format for a single entry.
    # start reading at byte after receiver info
    stb= i + offset
    ifoff = 0
    recstat['ifnoiseentries'] = []
    for recn in range(recstat['numactiverec']*2):
        recstat['ifnoiseentries'].append(readIFnoise(b, h, stb))
        ifoff += 11
    # The length of the receier section varies, so return also the next byte index
    # to enable further parsing of the following sections
    nextbyte = stb+ifoff 
    return recstat, nextbyte

def parse_metdata(b,h, i):
    # Table 4.4.21.11 Met Status
    # Note, updates usually every 5 seconds, so mjds only changes every 5 sec
    met = {}
    met["mjds"] = b2d(b,i)
    met["wind"] = b2d(b,i+2)
    met["meanwind"] = b2d(b,i+4)
    met["peakwind"] = b2d(b,i+6)
    met["winddir"] = b2d(b,i+8)
    met["meanwinddir"] = b2d(b,i+10)
    met["rain"] = b2d(b,i+12)
    met["drytemp"] = b2d(b,i+14)
    met["drytempRMS"] = b2d(b,i+16)
    met["pressure"] = b2d(b,i+18)
    met["pressureRMS"] = b2d(b,i+20)
    met["relhum"] = b2d(b,i+22)
    met["relhumRMS"] = b2d(b,i+24)
    met["watercoldens"] = b2d(b,i+26)
    met["electroncoldens"] = b2d(b,i+28)
    nextbyte = i + 30
    return met, nextbyte

def joinMcast(mcast_addr,port,if_ip):
    """
    Returns a live multicast socket
    mcast_addr is a dotted string format of the multicast group
    port is an integer of the UDP port you want to receive
    if_ip is a dotted string format of the interface you will use
    """
    
    print("""Will attempt to listen to multicast assuming, this computer has a
            network interface with the 192-network IP """ + if_ip + """. If no
            data, change iface_ip variable to right IP for this computer AND
            make sure port 7022 is open (e.g. ufw allow 7022).""")

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

#from astropy import units as u
#from astropy.coordinates import Angle
#def rad2dhms(rad):
#    angles = Angle(rad, unit=u.rad).to_string(unit=u.degree)
#    return " ".join(angles)

def print_teldata(td):
    if td['status']:
        arec = td['status']['receiverstatus']['currentrec']
        act = np.array(td['status']['actual_azel'][0:2])*180/np.pi
        dem = np.array(td['status']['demanded_azel'][0:2])*180/np.pi
        toprint = td['status']['time_isot'], "Binary length", td['binary_message_length'], td['telname'], td['status']['control'], "Az ", act[0], " dem ", dem[0], " El ", act[1], " dem ", dem[1],"Receiver: ", arec
    else:
        toprint = td['telname'], td['telnumber'], 'NOSTATUS'
    print(toprint)


if __name__ == "__main__":
    print("Running hsl2lib standalone, will parse binary stream...")
    # If DEBUG, allow exceptions to stop code. If False, catch exceptions and
    # only print ERROR: line.
    DEBUG = False
    
    # Configuration
    mcast_port  = 7022
    mcast_group = "239.0.0.254"
    iface_ip    = get_192IP()
    
    # Connect to socket
    msock = joinMcast(mcast_group, mcast_port, iface_ip)
    
    # Create empty dictionary to store telescope status data
    teldata = {}
    while True:
        # Read data
        binary = msock.recv(4096)
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
                utcnow = datetime.datetime.utcnow().isoformat()
                print("{0} UTC: Received {1} bytes of HSL2 data for {2}".format(utcnow, teldatum['binary_message_length'], teldatum['telname']))
                teldata[teldatum['telname']] = teldatum
                #if "Cam" in teldatum['telname']:
                #    print_teldata(teldatum)
    msock.close()
