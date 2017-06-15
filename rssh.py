#!/usr/bin/env python
# -*- coding: utf8 -*-

# блокировка до тех пор, пока не будет соединения с интернетом
from other_functions import wait_internet
wait_internet()
print 'internet'
# ==========================================================================================================
# https://ru.stackoverflow.com/questions/225896/%D0%97%D0%B0%D0%BF%D1%83%D1%81%D0%BA-bash-%D0%B8%D0%B7-%D1%81%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%B0-python-2-7-3
import subprocess
p = subprocess.Popen(['/home/pi/autocopter/build/rssh.sh'], subprocess.PIPE)
print 'smirart.ru:2202'
p2 = subprocess.Popen(['/home/pi/autocopter/build/rssh2.sh'], subprocess.PIPE)
print 'smirart.ru:5760'
#p = subprocess.Popen(['/home/pi/autocopter/build/rssh.sh'], stdout=subprocess.PIPE)
#p2 = subprocess.Popen(['/home/pi/autocopter/build/rssh2.sh'], stdout=subprocess.PIPE)
#line = p.stdout.readline()
#print line.strip()
#line2 = p2.stdout.readline()
#print line2.strip()
# line = p.stdout.readline()
# потом переделать под это https://pythonworld.ru/moduli/modul-subprocess.html
# ==========================================================================================================
while 1:
    import time
    time.sleep(10)
    pass