#!/usr/bin/env python
# -*- coding: utf8 -*-

from other_functions import wait_internet
# ожидание интернет подключения
wait_internet()
print 'internet'

# ==========================================================================================================
# https://ru.stackoverflow.com/questions/225896/%D0%97%D0%B0%D0%BF%D1%83%D1%81%D0%BA-bash-%D0%B8%D0%B7-%D1%81%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%B0-python-2-7-3
import subprocess, time
try:
    # https://pythonworld.ru/moduli/modul-subprocess.html
    #p = subprocess.call("ssh -N -R 2202:localhost:22 -i /home/pi/.ssh/id_rsa urpylka@smirart.ru -p32122", shell=True)
    p = subprocess.Popen(['/home/pi/autocopter/build/rssh.sh'], stdout=subprocess.PIPE)
    print 'smirart.ru:2202'
    p2 = subprocess.Popen(['/home/pi/autocopter/build/rssh2.sh'], stdout=subprocess.PIPE)
    print 'smirart.ru:5760'
    # потом переделать под это https://pythonworld.ru/moduli/modul-subprocess.html
    # ==========================================================================================================
    while True:
        time.sleep(4)
finally:
    # https://pythonworld.ru/moduli/modul-subprocess.html
    p.kill()
    p2.kill()
