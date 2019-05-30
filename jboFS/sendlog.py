#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys, os
import datetime

# NOTE: Needs the sshpass program to be installed by e.g. apt-get install sshpass

# Define station
st = 'jb'
vpass = 'PASSWORD' # Password for vlbeer server

def print_usage():
    print('sendlog.py - Upload logfile from FS to VLBEER server,')
    print('             assuming target dir is current month.')
    print('USAGE:   sendlog.py exp')
    print('EXAMPLE: sendlog.py n19l1{0}'.format(st))
    print('NOTE:    Assumed to be executed by FS procedure as')
    print('         sy =exec python /usr2/st/bin/sendlog.py `lognm` &')

def upload_log(exp):
    now = datetime.datetime.now() # Get current date and time
    mon = now.strftime("%b").lower() # e.g. mar for March
    yy = str(now.year)[-2:] # e.g. 19 for 2019
    vlbeerdir = '~/vlbi_arch/{0}{1}/'.format(mon,yy)
    log = '/usr2/log/{0}.log'.format(exp)
    outfile = '{0}.log'.format(exp)
    # Sometimes snp and prc files are renamed to exclude the station code, e.g.
    # n19l1jb-> n19l1. In such cases, we need to ensure the uploaded file
    # includes the station code
    if not '{0}.log'.format(st) in outfile:
        outfile = outfile.replace('.log','{0}.log'.format(st))
    if os.path.exists(log):
        # Transfer logfile to vlbeer
        cmd = 'sshpass -p "{0}" scp {1} evn@vlbeer.ira.inaf.it:{2}{3} 2>&1'.format(vpass, log,vlbeerdir,outfile)
        os.system(cmd)
        # Add comment in log about transfer
        cmd2 = "inject_snap '\"Logfile {0} transferred to vlbeer:{1}{2}.'".format(log,vlbeerdir,outfile)
        os.system(cmd2)
    else:
        print('Logfile {} not found, so not transferred to vlbeer.'.format(log))

if __name__ == "__main__":
    if len(sys.argv)!=2 :
        print_usage()
    else:
        exp = sys.argv[1]
        if exp == '-h' or exp == '--help':
            print_usage()
        else:
            upload_log(exp)
