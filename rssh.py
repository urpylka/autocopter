#!/usr/bin/env python
# -*- coding: utf8 -*-

# блокировка до тех пор, пока не будет соединения с интернетом
from other_functions import wait_internet
wait_internet()
print 'internet'
# ==========================================================================================================
# https://ru.stackoverflow.com/questions/225896/%D0%97%D0%B0%D0%BF%D1%83%D1%81%D0%BA-bash-%D0%B8%D0%B7-%D1%81%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%B0-python-2-7-3
import subprocess, time

try:
    while True:
        try:
            # https://pythonworld.ru/moduli/modul-subprocess.html
            p = subprocess.Popen(['/home/pi/autocopter/build/rssh.sh'], subprocess.PIPE)
            print 'smirart.ru:2202'
            p2 = subprocess.Popen(['/home/pi/autocopter/build/rssh2.sh'], subprocess.PIPE)
            print 'smirart.ru:5760'
            # потом переделать под это https://pythonworld.ru/moduli/modul-subprocess.html
            # ==========================================================================================================
            while True:
                time.sleep(10)
        except Exception as ex:
            print ex.message + '\n'
            time.sleep(4)
        finally:
            # https://pythonworld.ru/moduli/modul-subprocess.html
            p.kill()
            p2.kill()
finally:
    # https://pythonworld.ru/moduli/modul-subprocess.html
    p.kill()
    p2.kill()