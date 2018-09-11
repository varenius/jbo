#!/usr/bin/env python3
import socket, time, sys
import xml.etree.ElementTree as ET
import numpy as np
import curses
import math
from datetime import datetime
from curses import wrapper

otcx_ip='192.168.101.3'
otcx_port=7024
ns = {'jb': 'http://www.jb.man.ac.uk/emerlin/schema',}
rad2deg = (180.0/np.pi)

def deg2hms(deg):
    h = math.floor(deg*12.0/180)
    m = math.floor((deg*12.0/180-h)*60)
    s = ((deg*12.0/180-h)*60-m)*60
    h = str(int(h)).rjust(2,'0')
    m = str(int(m)).rjust(2,'0')
    s = str(round(s,5)).rjust(2,'0')
    return '{0}:{1}:{2}'.format(h,m,s)

def deg2txt(deg):
    d = math.floor(deg)
    arcm = math.floor((deg-d)*60)
    arcs = ((deg-d)*60-arcm)*60
    d = str(int(d)).rjust(2,'0')
    arcm = str(int(arcm)).rjust(2,'0')
    arcs = str(round(arcs,4)).rjust(2,'0')
    return '{0}:{1}:{2}'.format(d,arcm,arcs)

def init(stdscr, telescope):
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((otcx_ip,otcx_port))
    xml='<?xml version=\"1.0\"?>'
    xml+='<status_request telescope_id=\"{0}\">'.format(telescope)
    xml+='<statuses>on</statuses>'
    xml+='<part>allocation</part>'
    xml+='<part>pointing</part>'
    xml+='<part>receiver</part>'
    xml+='</status_request>'
    s.send(xml.encode())
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    lastlogged = ""
    while True:
        # A check for instrument_id is needed, since sometimes a response only contains e.g. this:
#'<?xml ion="1.0" encoding="UTF-8" standalone="no" ?> <instrument_status xmlns="http://www.jb.man.ac.uk/emerlin/schema" instrument_id="Control Room" instrument_number="2" time_stamp="5035787600" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.jb.man.ac.uk/emerlin/schema file:///home/rgn/develop/emer/trunk/otcx/schemata/emerlin/telescope_control.xsd">   <status>running</status>   <host>otcx</host> </instrument_status> '
        # which is not what we've asked for. If we get this, don't parse it
        #if not "instrument_id=\"Control Room\"" in str(resp):
        # However, we may also get other parse-errors, e.g. xml.parsers.expat.ExpatError and xml.etree.ElementTree.ParseError
        # Since we don't care about every second of data here, easiest solution is just to ignore these errors and carry on.
        # Therefore, a try:except statement wraps this whole update loop to keep it running. Error will displayed last if present.
        try: 
            resp = recall(s)
            root = ET.fromstring(resp)
            for actual in root.findall('jb:actual', ns):
                caz = rad2deg*float(actual.find('jb:longitude', ns).text)
                cal = rad2deg*float(actual.find('jb:latitude', ns).text)
            for demanded in root.findall('jb:demanded', ns):
                daz = rad2deg*float(demanded.find('jb:longitude', ns).text)
                dal = rad2deg*float(demanded.find('jb:latitude', ns).text)
            for coords in root.findall('jb:coords', ns):
                eq1 = rad2deg*float(coords.find('jb:longitude', ns).text)
                eq2 = rad2deg*float(coords.find('jb:latitude', ns).text)
                csys = coords.find('jb:coordinate_system', ns).text

            # Find current controller, e.g. e_Merlin
            ctrl = root.find('jb:allocation', ns).find('jb:controller', ns).text

            # Get number of active receiver
            recstat = root.find('jb:receiver_statuses', ns)
            arec = recstat.find('jb:active_receivers', ns)
            car = arec.find('jb:carousel', ns)
            arecnum = car.find('jb:receiver_number', ns).text

            # Get name of active receiver, e.g. "L-band"
            recstat = root.find('jb:receiver_statuses', ns)
            recstat2 = recstat.find('jb:receiver_statuses', ns)
            recstat3 = recstat2.find('jb:receiver_status', ns)
            recid = recstat3.find('jb:receiver_id', ns)
            recname = recid.find('jb:name', ns).text

            # Get LO frequencies
            recstat = root.find('jb:receiver_statuses', ns)
            recstat2 = recstat.find('jb:receiver_statuses', ns)
            recstat3 = recstat2.find('jb:receiver_status', ns)
            rconf = recstat3.find('jb:config', ns)
            los = rconf.find('jb:los', ns)
            lonums = []
            lofreqs = []
            for i,lo in enumerate(los.findall('jb:lo', ns)):
                freq = lo.find('jb:frequency', ns).text
                lonums.append(i)
                lofreqs.append(float(freq))
            utcnow = datetime.utcnow()
            doy= utcnow.timetuple().tm_yday
            lo32 = [32*i for i in lofreqs]
            stdscr.clear()
            stdscr.addstr(0, 0, "ANTENNA MONITOR")
            stdscr.addstr(1, 0, "UTC        : {0}".format(str(utcnow)))
            stdscr.addstr(2, 0, "Day number : {0}".format(str(doy).rjust(3,'0')))
            stdscr.addstr(3, 0, "Telescope  : {0}".format(telescope))
            stdscr.addstr(4, 0, "Allocation : {0}".format(ctrl))
            stdscr.addstr(5, 0, "Receiver   : {0}".format(recname))
            stdscr.addstr(6, 0, "Sky target : {0} | {1} SYS={2}".format(deg2hms(eq1),deg2txt(eq2),csys))
            stdscr.addstr(7, 0, "Current    : alt={0:.4f} az={1:.4f}".format(cal,caz))
            stdscr.addstr(8, 0, "Demanded   : alt={0:.4f} az={1:.4f}".format(dal,daz))
            stdscr.addstr(9, 0, "MERLIN LOs : {0} [Hz]".format(','.join([str(i) for i in lofreqs])))
            xml = True
        except Exception as e:
            xml = False
            err = str(e)
        if xml:
            stdscr.addstr(10, 0, "XML-link   : Valid")
            if abs(dal-cal)<0.01 and abs(daz-caz)<0.1:
                tolog = ctrl+" ONSOURCE"
            else:
                tolog = ctrl+" OFFSOURCE"
            # Get the date string, to use as logfile name
            utcnowdate = utcnow.strftime("%Y%m%d")
            logfile = open(telescope.replace(" ","_")+"." + utcnowdate + ".log","a")
            if not tolog == lastlogged:
                logfile.write(str(utcnow) + ": " + tolog + "\n")
                lastlogged = tolog
            logfile.close()
        else:
            stdscr.addstr(10, 0, "XML-link   : Invalid: ERROR: " + err)
        stdscr.refresh()

def has_end(text):
    endtags = [b'</telescope_status>',b'</instrument_status>']
    end = False
    for et in endtags:
        if et in text:
            end=True
    return end

def recall(s, nb=1024):
    msg = b''
    while True:
        part = s.recv(1024)
        msg +=part
        if has_end(msg):
            break
    return msg

wrapper(init, telescope = sys.argv[1])
#wrapper(init, telescope = "Pi")
