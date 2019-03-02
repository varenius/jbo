import re
import calendar
import os
# Auto-status page generator. Quick summary of logic:
# wget http://old.evlbi.org/scheduling/EVNschedule.txt
# rsync sched, proc from FS
# parse schedule, sched, proc
# wget log, antabfs, feedback page from vlbeer
# Check all the above, then write HTML
# needs key-login (no password) to faraday

def get_snp():
    os.system('rm ./snp/*jb.snp')
    os.system('rsync faraday.ast.man.ac.uk:/usr2/sched/*.snp ./snp/')

def get_prc():
    os.system('rm ./prc/*jb.prc')
    os.system('rsync faraday.ast.man.ac.uk:/usr2/proc/*.prc ./prc/')

def get_sch(exp, mon, yy):
    d = './sch/'
    if not os.path.exists(d):
        os.mkdir(d)
    fn = exp.lower()+'sch.jb'
    os.system('rm '+d+fn+'*')
    os.system('wget ftp://vlbeer.ira.inaf.it/vlb_arc/ftp/vlbi_arch/'+mon+yy+'/'+fn+'  -P '+d)

def check_log(exp, mon, yy, clear=False):
    # check ftp://vlbeer.ira.inaf.it/vlb_arc/ftp/vlbi_arch/mar19/n19c1jb.log
    d = './log/'
    if not os.path.exists(d):
        os.mkdir(d)
    fn = exp.lower()+'jb.log'
    if clear:
        os.system('rm '+d+fn+'*')
    if not os.path.exists(d + fn):
        os.system('wget ftp://vlbeer.ira.inaf.it/vlb_arc/ftp/vlbi_arch/'+mon+yy+'/'+fn+'  -P '+d)
    if os.path.exists(d + fn):
        return True
    else:
        return False
        
def check_antabfs(exp, mon, yy, clear=False):
    # check ftp://vlbeer.ira.inaf.it/vlb_arc/ftp/vlbi_arch/mar19/n19c1jb.antabfs
    d = './antabfs/'
    if not os.path.exists(d):
        os.mkdir(d)
    fn = exp.lower()+'jb.antabfs'
    if clear:
        os.system('rm '+d+fn+'*')
    if not os.path.exists(d + fn):
        os.system('wget ftp://vlbeer.ira.inaf.it/vlb_arc/ftp/vlbi_arch/'+mon+yy+'/'+fn+'  -P '+d)
    if os.path.exists(d + fn):
        return True
    else:
        return False

def get_feedback(exp, mon, yy, clear=False):
    # Get feedback page from e.g. http://old.evlbi.org/session/feb19/n19m1.html
    d = './feedback/'
    if not os.path.exists(d):
        os.mkdir(d)
    fn = exp.lower()+'.html'
    if clear:
        os.system('rm '+d+fn+'*')
    if not os.path.exists(d + fn):
        os.system('wget http://old.evlbi.org/session/'+mon+yy+'/'+fn+'  -P '+d)

def check_feedback(exp):
    # Check if feedback has been left for this experiment
    d = './feedback/'
    fn = exp.lower()+'.html'
    status = False
    # Check if file exists, if not return false
    try: 
        lines = [line.rstrip('\n') for line in open(d+fn)]
        for line in lines:
            if 'Jodrell_Bank' in line:
                status = True
                break
    except IOError as ioe:
        # File not found, so return fals for all results
        pass
    return status

def check_prc(exp, tel):
    # Check if file exists, if not return false
    d = './prc/'
    fn1 = exp.lower()+'jb.prc'
    fn2 = exp.lower()+'.prc'
    if os.path.exists(d + fn1):
        f = fn1
    elif os.path.exists(d + fn2):
        f = fn2
    else:
        f = None
    if f:
        lines = [line.rstrip('\n') for line in open(d + f)]
        #  file exists, parse lines to get the patching and LO value written by DRUDG
        for line in lines:
            if 'ifa=' in line:
                patch = line.split('=')[1][0]
            if 'lo=loa' in line:
                LO = line.split(',')[1][0:4]
        # parse lines to see if one of the contains the setup call,
        # this is manually added an may have been forgotten. It is e.g. 'set5664-mk2'.
        mod = ''
        for line in lines:
            if re.match('set[0-9]{4}-', line):
                mod = line
                break
        #Check if patching found above is correct for the scheduled telescope
        if tel=='Jb1':
            patchans = '1'
            modans = 'set' + LO + '-lt'
        elif tel=='Jb2':
            patchans = '2'
            modans = 'set' + LO + '-mk2'
        # Return bool1, bool2, bool3.
        # bool1 = prc file exists, bool2 = patching correct, bool3 = setLO-line correct
        return [True, patchans==patch, modans==mod, LO]
    else:
        # File not found, so return false for all results
        return [False, False, False, 0]

def check_snp(exp, tel):
    # Check if file exists, if not return false
    d = './snp/'
    fn1 = exp.lower()+'jb.snp'
    fn2 = exp.lower()+'.snp'
    if os.path.exists(d + fn1) or os.path.exists(d + fn2):
        return True
    else: 
        return False

# Make dictionary to translate month numbers to three letter abbreviations
md = {k: v.lower() for k,v in enumerate(calendar.month_abbr)}

d = './'
EVNfile = 'http://old.evlbi.org/scheduling/EVNschedule.txt'
locf = EVNfile.split('/')[-1]
if os.path.exists(d + locf):
    os.remove(locf)
os.system('wget ' + EVNfile + ' -P ' + d)

lines = [line.rstrip('\n') for line in open('./EVNschedule.txt')]
sess = ' '.join(lines[0].split()[3:6])
yr = sess[-2:]
if ' 1 ' in sess:
    sessmonth = 'feb'
elif ' 2 ' in sess:
    sessmonth = 'jun'
elif ' 3 ' in sess:
    sessmonth = 'oct'

# Get snp and prc files from farday
get_snp()
get_prc()
expdata = []
for line in lines:
    # Check if the line contains a timerange e.g. 1400(11/03)-2200(11/03)
    # If so, we can use the line to get antenna list etc. Other lines are ignored.
    pattern = '[0-9]{4}\([0-9]{2}\/[0-9]{2}\)-[0-9]{4}\([0-9]{2}\/[0-9]{2}\)'
    res = re.search(pattern, line)
    # Check if Jb1 or Jb2 in experiment, otherwise ignore line
    jb = re.search('Jb[1-2]{1}', line)
    if (res and jb):
        # Add spaces around brackets for stations and split.
        # Spaces needed to line item count correct for slicing stations
        ls = line.replace('[',' [').replace(']','] ').split()
        exp = ls[0]
        day = ls[29]
        jbtel = jb.group(0)
        antennas = ''.join(ls[1:25]).replace('-', '')
        dt = res.group(0)
        mi = int(dt[8:10])
        ms = md[mi]
        sch = exp+'scn.jb'
        prc = exp+'jb.prc'
        snp = exp+'jb.snp'

        #if exp =='N19C1' or exp=='ED044':
        if True:
            get_feedback(exp, sessmonth, yr)
            expdata.append([exp, antennas, check_prc(exp, jbtel), check_snp(exp, jbtel), check_feedback(exp), check_log(exp, ms, yr), check_antabfs(exp, ms, yr)])
            if exp =='N19M1':
                print expdata[-1]
            #['N19C1', 'Jb2Wb1EfMcNtOn85T6UrTrYsHhSvZcBdIr', (True, True, True, '5664'), True, False, True, True]


def format_tabdata(ed):
    s = ''
    for d in ed:
        s += '    <tr>\n'
        s += '      <td>{0}</td>\n'.format(d[0])
        s += '      <td>{0}</td>\n'.format(d[1].replace('MER','<b>MER</b>').replace('Jb1','<b>Jb1</b>').replace('Jb2','<b>Jb2</b>'))
        # Check if PRC file is OK
        if d[0][0:2]=='CL':
            s += '      <td>{0}</td>\n'.format('N/A')
        elif all(d[2]):
            s += '      <td>{0}</td>\n'.format('OK')
        elif d[2][0]:
            s += '      <td>{0}</td>\n'.format('CHECK!')
        else:
            s += '      <td>{0}</td>\n'.format('-')
        # Check if SNP file is OK
        if d[0][0:2]=='CL':
            s += '      <td>{0}</td>\n'.format('N/A')
        elif d[3]:
            s += '      <td>{0}</td>\n'.format('OK')
        else:
            s += '      <td>{0}</td>\n'.format('-')
        # Check if Feedback is OK
        if d[4]:
            s += '      <td>{0}</td>\n'.format('OK')
        else:
            s += '      <td>{0}</td>\n'.format('-')
        # Check if Logfile is OK at vlbeer
        if d[0][0:2]=='CL':
            s += '      <td>{0}</td>\n'.format('N/A')
        elif d[5]:
            if d[0]=='N19C1':
                print d, 'OK'
            s += '      <td>{0}</td>\n'.format('OK')
        else:
            s += '      <td>{0}</td>\n'.format('-')
        # Check if antabfs is OK at vlbeer
        if d[0][0:2]=='CL':
            s += '      <td>{0}</td>\n'.format('N/A')
        elif d[6]:
            s += '      <td>{0}</td>\n'.format('OK')
        else:
            s += '      <td>{0}</td>\n'.format('-')

        s += '    </tr>\n'
    return s

def format_tabheader():
    h = '    <tr>\n'
    h += '      <th>Exp</th>\n'
    h += '      <th>Antennas</th>\n'
    h += '      <th>PRC@FS</th>\n'
    h += '      <th>SNP@FS</th>\n'
    h += '      <th>Feedback@JIVE</th>\n'
    h += '      <th>LOG@vlbeer</th>\n'
    h += '      <th>antabfs@JIVE</th>\n'
    h += '    </tr>\n'
    return h

header = '<!doctype html>\n'
header += '<html lang="en">\n'
header += '<head>\n'
header += '  <meta charset="utf-8">\n'
header += '  <title>Jb VLBI status</title>\n'
header += '  <link rel="stylesheet" href="css/styles.css">\n'
header += '</head>\n'
body = '<body>\n'
body += '<h1>{0}</h1>\n'.format('Jodrell Bank VLBI friend auto-checklist for '+sess)
body += 'Note: This page is preliminary and should not be trusted. Ask Eskil for details. \n'
#body += '  <script src="js/scripts.js"></script>\n'
body += '<table id=experiments>\n'
body += '  <thead>\n'
body += format_tabheader()
body += '  </thead>\n'
body += '  <tbody>\n'
body += format_tabdata(expdata)
body += '  </tbody>\n'
body += '</table>\n'
body += '</body>\n'
footer = '</html>'
of = open('./index.html','w')
of.write(header)
of.write(body)
of.write(footer)
of.close()
