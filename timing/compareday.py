import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time as atime
import os
# Select comparison date
date = '20180806'
logname = date + '.log'

#JBO VLBI GPS1PPS vs 5MHz1PPS log file
#Prologix GPIB-USB Controller version 6.107
#HEWLETT-PACKARD,53131A,0,3944
#GPIBADDR=3
#UTCDATE UTCTIME GPS1PPS-5MHz1PPS[seconds]

#LP
# Logfile made from measurements of Less new box, measured by tycho
lplog = logname + '.tycho'
os.system('scp /home/oper/timing/LESTEST/logs/'+logname + ' ' + lplog)
LP = []
for line in open(lplog):
    if not line.startswith('#'):
        ls = line.split()
        time = ls[0] + " " + ls[1]
        #mjd = atime(time, format='iso', scale='utc').mjd
        unix = atime(time, format='iso', scale='utc').unix
        LP.append([float(unix), float(ls[2])*1e6])

# PB
# Logfile made from measurements of the old Paul Burgess box, measured by goedel
pblog = logname + '.goedel'
os.system('scp goedel:/home/oper/timing/logs/'+logname + ' ' + pblog)
PB = []
for line in open(pblog):
    if not line.startswith('#'):
        ls = line.split()
        time = ls[0] + " " + ls[1]
        #mjd = atime(time, format='iso', scale='utc').mjd
        unix = atime(time, format='iso', scale='utc').unix
        PB.append([float(unix), float(ls[2])*1e6])

LP = np.array(LP)
PB = np.array(PB)
print(LP)
print(PB)

plt.plot(PB[:,0], PB[:,1],label = "Old box")
plt.plot(LP[:,0], LP[:,1]+0.6,label = "New + 0.6us")
#plt.plot(LP[:,0], LP[:,1],label = "New")
plt.xlabel("Time [seconds]")
plt.ylabel("GPS 1PPS - 5MHZ 1PPS [us]")
plt.ylim([-5,0])
plt.legend()
plt.show()
