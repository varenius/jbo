import os
from calendar import monthrange, month_abbr
from astropy.time import Time as atime
import numpy as np
import sys
from datetime import datetime, timedelta

def printUsage():
    print("USAGE: makegps.py LOGDIR UPLOAD YYYY MM ")
    print("       e.g. vlbilog.py /home/oper/timing/logs/ YES 2018 04")
    print("       will write the logfile g04_2018.jb and upload to evn@vlbeer.ira.inaf.it:gps/mar18/gps.jb")
    print("       e.g. vlbilog.py /home/oper/timing/logs/ NO will create file but will not upload 2018 04")
    print("       NOTE: YYYY and MM are optional and default value is the month of yesterday. I.e. running the script")
    print("       April 1st will process data for March the same year. Manual dates override.")

if len(sys.argv)<3:
    printUsage()
    sys.exit()
# Will look for logfiles in the logdir specified last
logdir = sys.argv[1]
# Ensure logdir exists
os.system("mkdir -p "+logdir)
# Store the files made by this script in the outdir
outdir = "/home/oper/timing/tovlbeer/"
# Ensure outir exists
os.system("mkdir -p "+outdir)
if sys.argv[2]=="YES":
    upload = True
else:
    upload = False

# Get current date time string, used for logging purposes
utcnow = datetime.utcnow()

# Year and month given as arguments, or default to yesterday's values
try: 
    year = int(sys.argv[3])
    month = int(sys.argv[4])
except IndexError:
    procdate = utcnow - timedelta(days=1)
    year = int(procdate.year)
    month = int(procdate.month)

# Define outfile name, e.g. g03_2018.jb for March 2018
outfn = outdir + "g"+str(month).rjust(2,"0") + "_"+str(year)+".jb"
#print("Writing GPS-log file "+ outfn)


# Check if output file exists, if so move it to a backup file
if os.path.exists(outfn):
    oldname = outfn + ".old."+str(utcnow).replace(" ","_").replace(":","_")
    print(outfn + " already exists! Renaming to " + oldname)
    os.system("mv " + outfn + " " + oldname)

# Write header to output file
outf = open(outfn, "w")
outf.write("#Jodrell Bank VLBI GPS-maser log\n")
outf.write("#Created UTC " + str(utcnow) + "\n")
outf.write("#A negative offset means the maser clock lags behind the GPS clock\n")
outf.write("#MJD offset[us] RMS[us] comment\n")

data = []
# Figure out how many days are in this month
ndays = monthrange(year, month)[1]

# Now, for each day, load the logfile
for day in range(1,ndays+1):
    # Load high-resolution log file for this day
    try:
        hrf = logdir + "/" + str(year)+str(month).rjust(2,"0")+str(day).rjust(2,"0") + ".log"
        hrfdata = open(hrf)
        #Logfile lines are formated (# marks comment lines) as
        #2018-04-09 00:00:00.763474 -6.258e-07
        # Read values from this file and store in lists
        times = []
        vals = []
        for line in hrfdata:
            if not ("#" in line):
                ls = line.strip().split(" ")
                #print(ls)
                times.append(ls[0] + " " + ls[1])
                vals.append(float(ls[2]))
        # Calculate MJD times from these timestamps
        mjds = atime(times, format='iso', scale='utc').mjd
        # Calculate average MJD, average value, and standard deviation
        avgmjd = np.average(mjds)
        avgval = np.average(vals)
        stdval = np.std(vals)
        # Format the output values properly
        mjdstr = str(round(avgmjd,3)).ljust(9,"0")
        valstr = str(round(avgval*1e6,3)).ljust(6,"0")
        stdstr = str(round(stdval*1e6,3)).ljust(5,"0")
        comment = "GPSJBV"
        #print(mjdstr, valstr, stdstr)
        # Check if RMS is more than 100ns, if so something is likely wrong (e.g. clock reset)
        # and we should write the value as a commented line
        if stdval > 0.1e-6:
            outf.write("#{0} {1} {2} {3}\n".format(mjdstr, valstr, stdstr,comment))
        else:
            outf.write("{0} {1} {2} {3}\n".format(mjdstr, valstr, stdstr,comment))
    except FileNotFoundError:
        # If this day does not have a logfile, skip this date (perhaps not yet written)
        #print("File " + hrf + " not found. Skipping this date.")
        pass
outf.close()

if upload:
    evndir = month_abbr[int(month)].lower() + str(year)[-2:]
    cmd = "scp {0} evn@vlbeer.ira.inaf.it:gps/{1}/gps.jb".format(outfn,evndir)
    #print("Running command: "+cmd)
    os.system(cmd)
