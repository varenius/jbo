import stadi
import time
from datetime import datetime
import os

# INSTRUCTIONS
# This script should be running continuously in a "screen" as e.g. user oper
# to log timing data to log files. The log files can (periodically) be processed
# to yield averaged or re-formatted timing data for e.g. VLBI/Pulsar use.

# START OF CONFIG
# Ouput log directory
logdir = "/home/oper/maserlogging/logs"
# GPIB address of GPIB unit used to read data
gpibaddr = '20'
# USB port used, check "dmesg" when connecting USB-to-GPIB 
# unit to discover which e.g. /dev/ttyUSB0 and then udev rules
# to assign that particular unit to a permanent /dev/name symlink
USB = "/dev/USBGPIB1"
# END OF CONFIG

# Ensure logdir exists
os.system("mkdir -p "+logdir)
# Connect to measurement device
inst = stadi.ScpiInstrumentWrapper('PROLOGIX::'+USB+'::GPIB::'+gpibaddr)

# Define header to put in every new log file
header = "#JBO VLBI GPS1PPS vs 5MHz1PPS log file\n"
header += "#" + inst.query('++ver') + "\n"
header += '#' + inst.query('*IDN?') + "\n"
header += '#GPIBADDR=' + gpibaddr + "\n"
header += '#UTCDATE UTCTIME GPS1PPS-5MHz1PPS[seconds]' + "\n"

# Start infinite loop, script terminates with CTRL+C
while True:
    # Get current UTC timestamp
    utcnow = datetime.utcnow()
    # Get the date string, to use as logfile name
    utcnowdate = utcnow.strftime("%Y%m%d")
    # Set logfile name
    outfile = logdir + "/" + utcnowdate+'.log'
    # Check if file exists. 
    if not os.path.isfile(outfile):
        # If not, we're starting a new file and
        # we should start with the header, so write this.
        of=open(outfile, 'a')
        of.write(header)
        of.close()
    else:
        # File exists, so append new data
        of=open(outfile, 'a')
        try:
            # Try to read value from GPIB. 
            val = inst.query('READ?')
            # Convert from positive delay measured 
            # From GPS1PPS to 5MHz1PPS to negative value 
            # Since we want GPS - 5MHz1PPS
            val = -1*float(val)
            of.write(str(utcnow) + ' ' + str(val) +'\n')
        except: 
            # GPIB READ may fail sometimes (rare), but e.g. if resuming
            # an already existing logfile after halting the script.
            # In that case write a commented line saying a read failed
            of.write("#" + str(utcnow) + ' FAILED GPIB READ\n')
            pass
        # Wait for GPIB device to allow new READ
        time.sleep(1.5)
        # Close outfile to ensure all data is flushed to disk.
        of.close()
