import re, datetime, sys
    
flexbuff3= {'dataip' : '192.168.81.76', 'datamac' : '00:07:43:11:fd:d8', 'comip': '192.168.101.43', 'combuffer':1024, 'comport':2620}
flexbuff2= {'dataip' : '192.168.81.77', 'datamac' : '00:07:43:11:fd:e8', 'comip': '192.168.101.42', 'combuffer':1024, 'comport':2620}

class vexfile:
    def __init__(self,infile,keytel):
        # Run a sequence of functions to parse and structure information in the vexfile
        self.infile = infile
        self.parse()
        self.getExp()
        self.getFreq(keytel)
        self.getScans(keytel)
        self.getSources()

    def parse(self):
        # Parse vex file to dictionary
        with open(self.infile) as f:
            content = f.readlines()
        content = [x.strip() for x in content] 
        
        self.vexdata = {}
        section = ''
        self.vexdata[section] = []
        for line in content:
            if line.startswith('$'):
                section = line.strip()
                self.vexdata[section] = []
            # Ignore comment lines marked '*'
            if not line.startswith('*'):
                self.vexdata[section].append(line.strip())

    def getExp(self):
        # Find exp code
        for line in self.vexdata['$GLOBAL;']:
            if 'ref $EXPER' in line:
                self.exp = line.split('=')[-1].strip(' ;')
                break

    def getFreq(self,freqtel):
        # Find frequency
        for line in self.vexdata['$MODE;']:
            if ('ref $FREQ' in line) and (freqtel in line):
                self.freq = re.split(r"[=M]", line)[1]
                break

    def getSources(self):
        # Build source catalogue with ras, decs, assuming J2000 for now
        self.sources = {}
        for line in self.vexdata['$SOURCE;']:
            if ('source_name' in line):
                name = re.split(r"[=;]", line)[1].strip()
            if ('J2000' in line):
                line = re.sub(r"[hdm']",':',line)
                pos = re.split(r"[=;]", line)
                ra = pos[1][:-1].strip()
                dec = pos[3][:-1].strip()
                if self.sourceInScans(name): 
                    self.sources[name] = [ra,dec]

    def getScans(self,scantel):
        # Read scan details
        self.scans = []
        for line in self.vexdata['$SCHED;']:
            if ('scan No' in line):
                scanid = re.split(r"[ ;]", line)[1]
                tmpscan = {}
                tmpscan['id']=scanid
                # Flag changed if scantel is found in the list of stations for this scan
                addscan = False
            if ('start' in line):
                scanstart = re.split(r"[=;]", line)[1]
                tmpscan['start'] = scanstart
                scansource= re.split(r"[=;]", line)[5]
                tmpscan['source'] = scansource
            if ('data_transfer' in line):
                if not 'ftp' in tmpscan.keys():
                    ftpstart = re.split(r"[=:]", line)[4].strip().split()[0]
                    ftpstop = re.split(r"[=:]", line)[5].strip().split()[0]
                    tmpscan['ftp'] = [ftpstart, ftpstop]
            if ('station' in line):
                station= re.split(r"[=:]", line)[1]
                dur= re.split(r"[=:]", line)[3].strip().split(' ')[0] # dur in seconds
                if station==scantel:
                    addscan = True
                    if not 'dur' in tmpscan.keys():
                        tmpscan['dur'] = dur
            if ('endscan' in line):
                if addscan:
                    self.scans.append(tmpscan)
    
    def sourceInScans(self,source):
        ans = False
        for scan in self.scans:
            if scan['source'] == source:
                ans = True
                break
        return ans

def makeConfig(vex, tels):

    of = open(vex.exp+'_Config.py','w')

    header = "#generated from {0}\n".format(vex.infile)
    header += "from uk.ac.man.jb.emerlin.ojd import *\n"
    header += "from uk.ac.man.jb.emerlin.correlatormodel import *\n"
    header += "from uk.ac.man.jb.emerlin.observation import *\n"
    header += "\n"
    of.write(header)

    #obs = "freq = ObservingFrequency.find('vlbi_L-band_nme') # ObservingFrequency 1.306490e+09 vlbi_L-band_nme \n"
    #obs = "freq = ObservingFrequency.find('n16m1') # ObservingFrequency 6.659490e+09 n16m1\n"
    #of1 = ObservingFrequency.find("n16m1")
    #of2 = ObservingFrequency(of1, "N18M1")
    #of2.fdef
    #of2.setEffectiveLO(6.61949e9)
    #of2.fdef
    #of2.save()

    obs = "freq = ObservingFrequency.find('"+vex.exp+"') # Make sure this frequency exists. If not, create from nearby one (or use another with baseband offset).\n"
    obs += "tels = " + str(tels) + "\n"
    obs += "basebands = [ BaseBandModel(0, freq, 8, 1.0, Polarization.code.Left, 8),\n"
    obs += "              BaseBandModel(1, freq, 8, 1.0, Polarization.code.Right, 8)]\n"
    obs += "obs = ObservationConfiguration(basebands)\n"
    obs += "obs.setBaselines(Telescope.allCross(Telescope.asList(tels),True))\n"
    obs += "obs.widarOffsetId='vlbi'\n"
    obs += "obs.delayApplyVDIF = True # apply a delay model - but note in OJDParameters it is possible to switch off the geometric part\n"
    obs += "obs.fringeRotateVDIF = False # generally VLBI seems to want to do this for itself\n"
    obs += "obs.setSubBand(4,32.e6,64e6) # DEFINE MANUALLY: Set or add second subband to be extracted, must be exactly 4 offset from the other one used. Pair defined below, e.g. 0,4 or 1,5.\n"
    obs += "\n"
    of.write(obs)
    
    sb0 = 0 # First subband to be extracted as VDIF, next will be sb0+4.
    for ncount, tel in enumerate(tels):
        if ncount<3:
            flexbuff = flexbuff2
        else:
            flexbuff = flexbuff3
        if tel=='Mk2':
            tel='MK2'
        of.write("obs.addVLBI(Telescope."+tel + ", "+str(sb0+4*(ncount//4))+ ", '" + flexbuff['dataip'] + "', '" + flexbuff['datamac'] + "')\n")

    of.write("\n")
    of.write("conf = SubArrayConfig.save('"+vex.exp+"conf', obs)")

    of.close()


def makeOJD(vex):
    of = open(vex.exp+'_OJD.py','w')
    header = "#generated from {0}\n".format(vex.infile)
    header += "from uk.ac.man.jb.emerlin.ojd import *\n"
    header += "from uk.ac.man.jb.emerlin.configuration import *\n"
    header += "from uk.ac.man.jb.emerlin.observation import Telescope\n"
    header += "from org.javastro.coord import JulianDate\n"
    header += "from ojd.OJDMisc import *\n"
    header += "import java.text.SimpleDateFormat\n"
    header += "import java.util.TimeZone\n"
    header += "\n"
    header += "vf = java.text.SimpleDateFormat(\"yyyy'y'D'd'HH'h'mm'm'ss's'\")\n"
    header += "vf.setTimeZone(java.util.TimeZone.getTimeZone('UTC'))\n"
    header += "ojd = OJD('{0}')\n".format(vex.exp)
    of.write(header)

    of.write("\n#sources to be observed\n")
    of.write("src = {}\n")
    for sour in sorted(vex.sources):
        ra = vex.sources[sour][0]
        dec = vex.sources[sour][1]
        of.write("src['"+sour + "'] = TargetSource('"+ra+ "','"+dec+"')\n")

    of.write("\n")
    of.write("#correlator config\n")
    conf ="sac = SubArrayConfig.find('{0}conf')\n".format(vex.exp)
    conf +="gac = GlobalConfig.DEFAULT\n"
    conf +="exp = Experiment(1, '{0}')\n".format(vex.exp)
    conf +="par =  OJDParameters().globalConfig(gac).subArrayConfig(sac).experiment(exp).stopIntegratingOffPosition(False).applyGeometricDelay(False).doTroposphericCorrection(False)\n"
    #conf +="exTel = ExcludedTelescope(Telescope.Lovell) # Does this do anything?\n" 
    of.write(conf)

    of.write("\n")
    of.write("#observations\n")
    for scan in vex.scans:
        of.write("ojd.add(Observation('" + scan['id'] + "', src['"+scan['source'] + "'],par).start(JulianDate(vf.parse('" + scan['start'] + "'))).duration('" + scan['dur'] + " sec'))\n")
    of.write("ojd.schedule()\n")
    of.write("ojd.fillGaps()\n")
    of.write("ojd.save()\n")
    of.write("print '\\n'.join([str(x) for x in ojd.scheduleDetail])\n")
    of.close()

def vlbitimeplusdt(vlbistring,dt):
    time = datetime.datetime.strptime(vlbistring, "%Yy%jd%Hh%Mm%Ss")
    dt = datetime.timedelta(seconds=dt)
    newstring = (time+dt).strftime("%Yy%jd%Hh%Mm%Ss")
    return newstring

def twoletter(telescope):
    tels = {'Darnhall':'Da', 'Pickmere':'Pi' , 'Mk2': 'Jm', 'Knockin' : 'Kn', 'Defford': 'De', 'Cambridge' : 'Cm', 'Lovell': 'Jl'}
    return tels[telescope]

def makeFTP(vex, tels, doubleSB = False):
    of = open(vex.exp+'_FTP.py','w')
    header = "#generated from {0}\n".format(vex.infile)
    #'''convert the time given in the vex file format to seconds since the epoch for use in sched'''
    of.write("import datetime, socket, sched, time, os\n")
    of.write("\n")
    of.write("def vlbitime2unix(vlbi_time):\n")
    of.write("    dt = datetime.datetime.strptime(vlbi_time, '%Yy%jd%Hh%Mm%Ss')\n")
    of.write("    return time.mktime(dt.timetuple())\n")
    of.write("\n")
    of.write("def flexbuffcmd(comip, comport, message):\n")
    of.write("    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n")
    of.write("    sock.connect((comip, int(comport)))\n")
    of.write("    sock.send(message)\n")
    of.write("    print('sent to '+comip+':'+comport + ': + message')\n")
    of.write("    data = sock.recv(1024)\n")
    of.write("    print(comip + 'answer: ', data)\n")
    of.write("    sock.close()\n\n")

    of.write("def autoftp(comip, fname):\n")
    of.write("    os.system('ssh oper@' + comip + ' ncftpput -p JBO 192.42.120.93 ftpdata /home/oper/data/' + fname)\n")
    of.write("s = sched.scheduler(time.time, time.sleep)\n")
    of.write("\n")
    for scan in vex.scans:
        for port,tel in enumerate(tels):
            #  Store first 3 data streams on flexbuff2, rest on flexbuff3
            if port<3:
                fb = flexbuff2
            else:
                fb = flexbuff3
            stel = twoletter(tel).lower()
            if 'ftp' in scan.keys():
                # Allow 30 sec for record and disk2file to finish.
                if doubleSB:
                    of.write("s.enterabs(vlbitime2unix('"+scan['start'] + "') + " + scan['dur'] + " + 30, 15, autoftp,('{1}_{0}_{2}.vdif',),)\n".format(stel+'0',vex.exp.lower(),scan['id'].lower()))
                    of.write("s.enterabs(vlbitime2unix('"+scan['start'] + "') + " + scan['dur'] + " +30, 15, autoftp,('{1}_{0}_{2}.vdif',),)\n".format(stel+'1',vex.exp.lower(),scan['id'].lower()))
                else:
                    of.write("s.enterabs(vlbitime2unix('"+scan['start'] + "') + " + scan['dur'] + " + 30, 15, autoftp,('{1}_{0}_{2}.vdif',),)\n".format(stel,vex.exp.lower(),scan['id'].lower()))
    of.write("for j in s.queue:\n")
    of.write("    print(j)\n")
    of.write("s.run()\n")
    of.close()

def makeFBUF(vex, tels, doubleSB = False):
    of = open(vex.exp+'_FBUF.py','w')
    header = "#generated from {0}\n".format(vex.infile)
    #'''convert the time given in the vex file format to seconds since the epoch for use in sched'''
    of.write("import urllib2, urllib\n")
    of.write("import datetime, socket, sched, time, os\n")
    of.write("\n")
    of.write("def vlbitime2unix(vlbi_time):\n")
    of.write("    dt = datetime.datetime.strptime(vlbi_time, '%Yy%jd%Hh%Mm%Ss')\n")
    of.write("    return time.mktime(dt.timetuple())\n")
    of.write("\n")
    of.write("def vdifAgcSet():\n")
    of.write("    URL = 'http://130.88.9.19:8080/console'\n")
    of.write("    req = urllib2.Request(URL, data=urllib.urlencode({'input':'correlator.vdifAgcSet()'}))\n")
    of.write("    response = urllib2.urlopen(req)\n")
    of.write("    the_page = response.read() # Not used\n\n")

    of.write("def flexbuffcmd(comip, comport, message):\n")
    of.write("    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n")
    of.write("    sock.connect((comip, int(comport)))\n")
    of.write("    sock.send(message)\n")
    of.write("    print('sent to '+comip+':'+comport + ': + message')\n")
    of.write("    data = sock.recv(1024)\n")
    of.write("    print(comip + 'answer: ', data)\n")
    of.write("    sock.close()\n\n")

    of.write("s = sched.scheduler(time.time, time.sleep)\n")
    of.write("\n")
    starttime = vex.scans[0]['start']
    of.write("# Set Agc on WIDAR correlator when first scan starts. vdifAgcSet will adapt and then stabilise.\n")
    of.write("s.enterabs(vlbitime2unix('"+starttime + "'), 1, vdifAgcSet,())\n")
    startstemp = "'runtime = {0} ; net_protocol = pudp : 32M : 256M : 8 ; mtu = 9000 ; net_port = 1300{3}  ; mode = VDIF_8000-512-1-2 ; record = on : {1}_{0}_{2}.vdif;'" # 0;tel, 1:exp, 2:scanid (no0001) 3:port-number 0,1,2...in the order telescopes are added, so in order of tel list
    stopstemp = "'runtime = {0} ; record = off ;'" # 0;tel
    ftpstemp = "'runtime = {0} ; scan_set={1}_{0}_{2}:{3}:{4} ; disk2file={1}_{0}_{2}.vdif ;'" # 0;tel, 1:exp, 2:scanid (no0001) 3:starttime, 4:start+2
    evlbitemp = "'runtime = {0} ; evlbi? ;'" # 0;tel
    for scan in vex.scans:
        for port,tel in enumerate(tels):
            #  Store first 3 data streams on flexbuff2, rest on flexbuff3
            if port<3:
                fb = flexbuff2
            else:
                fb = flexbuff3
            stel = twoletter(tel).lower()
            if doubleSB:
                # Use 0 (and 1 in other doubleSB clause below) at end of tel in filename
                startstring = startstemp.format(stel+'0',vex.exp.lower(),scan['id'].lower(),str(port))
                stopstring = stopstemp.format(stel+'0')
                evlbistring = evlbitemp.format(stel+'0')
            else:
                startstring = startstemp.format(stel,vex.exp.lower(),scan['id'].lower(),str(port))
                stopstring = stopstemp.format(stel)
                evlbistring = evlbitemp.format(stel)
            of.write("s.enterabs(vlbitime2unix('"+scan['start'] + "'), 15, flexbuffcmd,('{0}','{1}',{2}".format(fb['comip'], fb['comport'], startstring)+",),)\n")
            of.write("s.enterabs(vlbitime2unix('"+scan['start'] + "') + " + scan['dur'] + ", 10, flexbuffcmd,('{0}','{1}',{2}".format(fb['comip'], fb['comport'], stopstring)+",),)\n")
            of.write("s.enterabs(vlbitime2unix('"+scan['start'] + "') + " + scan['dur'] + ", 20, flexbuffcmd,('{0}','{1}',{2}".format(fb['comip'], fb['comport'], evlbistring)+",),)\n")
            if 'ftp' in scan.keys():
                if doubleSB:
                    # Use 0 (and 1 in other doubleSB clause below) at end of tel in filename
                    ftpstring = ftpstemp.format(stel+'0',vex.exp.lower(),scan['id'].lower(),vlbitimeplusdt(scan['start'],int(scan['ftp'][0])),vlbitimeplusdt(scan['start'],int(scan['ftp'][1])))
                else:
                    # no trailing 0
                    ftpstring = ftpstemp.format(stel,vex.exp.lower(),scan['id'].lower(),vlbitimeplusdt(scan['start'],int(scan['ftp'][0])),vlbitimeplusdt(scan['start'],int(scan['ftp'][1])))
                # Wait 5 seconds for record to finish, then run disk2file
                of.write("s.enterabs(vlbitime2unix('"+scan['start'] + "') + " + scan['dur'] + " + 5, 15, flexbuffcmd,('{0}','{1}',{2}".format(fb['comip'], fb['comport'], ftpstring)+",),)\n")
            if doubleSB:
                startstring = startstemp.format(stel+'1',vex.exp.lower(),scan['id'].lower(),str(port+4))
                stopstring = stopstemp.format(stel+'1')
                of.write("s.enterabs(vlbitime2unix('"+scan['start'] + "'), 15, flexbuffcmd,('{0}','{1}',{2}".format(fb['comip'], fb['comport'], startstring)+",),)\n")
                of.write("s.enterabs(vlbitime2unix('"+scan['start'] + "') + " + scan['dur'] + ", 10, flexbuffcmd,('{0}','{1}',{2}".format(fb['comip'], fb['comport'], stopstring)+",),)\n")
                if 'ftp' in scan.keys():
                    ftpstring2 = ftpstemp.format(stel+'1',vex.exp.lower(),scan['id'].lower(),vlbitimeplusdt(scan['start'],int(scan['ftp'][0])),vlbitimeplusdt(scan['start'],int(scan['ftp'][1])))
                    of.write("s.enterabs(vlbitime2unix('"+scan['start'] + "') + " + scan['dur'] + " + 5, 15, flexbuffcmd,('{0}','{1}',{2}".format(fb['comip'], fb['comport'], ftpstring2)+",),)\n")

    of.write("for j in s.queue:\n")
    of.write("    print(j)\n")
    of.write("s.run()\n")
    of.close()

    
def main(args):
    vex = vexfile(args[1], args[2])
    print(vex.scans)
    tels = ['Darnhall', 'Pickmere', 'Mk2', 'Knockin', 'Defford', 'Cambridge']
    #tels = ['Darnhall', 'Pickmere', 'Knockin', 'Defford', 'Cambridge']
    #tels = ['Darnhall', 'Pickmere', 'Knockin', 'Cambridge']
    makeConfig(vex,tels)
    makeOJD(vex)
    makeFBUF(vex,tels, doubleSB=False)
    #makeFTP(vex,tels, doubleSB=False)

if __name__ == "__main__":
    main(sys.argv)

