#!/usr/bin/python
# -*- coding: utf8 -*-

import http.client
from dronekit import connect, VehicleMode

def get_ip():
    conn = http.client.HTTPConnection("smirart.ru")
    conn.request("GET", "/ip")
    return conn.getresponse().read()

def get_status(vehicle):
    buf = "\nGPS: %s" % vehicle.gps_0 + \
          "\nBattery: %s" % vehicle.battery + \
          "\nLast Heartbeat: %s" % vehicle.last_heartbeat + \
          "\nIs Armable?: %s" % vehicle._is_armable + \
          "\nSystem status: %s" % vehicle.system_status.state + \
          "\nMode: %s" % vehicle.mode.name
    return buf

vehicle = connect('tcp:127.0.0.1:14600', wait_ready=True)
print "Сopter online: %s" % get_ip()
print get_status(vehicle)
vehicle.close()
