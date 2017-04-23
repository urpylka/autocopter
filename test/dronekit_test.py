#!/usr/bin/python
# -*- coding: utf8 -*-
def get_ip():
    import http.client
    conn = http.client.HTTPConnection("smirart.ru")
    conn.request("GET", "/ip")
    return conn.getresponse().read()
def get_status(vehicle):
    # Get some vehicle attributes (state)
    buf = "Get some vehicle attribute values:"+\
          "\nGPS: %s" % vehicle.gps_0+\
          "\nBattery: %s" % vehicle.battery+\
          "\nLast Heartbeat: %s" % vehicle.last_heartbeat+\
          "\nIs Armable?: %s" % vehicle.is_armable+\
          "\nSystem status: %s" % vehicle.system_status.state+\
          "\nMode: %s" % vehicle.mode.name    # settable
    return buf
# Import DroneKit-Python
from dronekit import connect, VehicleMode
# Connect to the Vehicle (in this case a UDP endpoint)
vehicle = connect('tcp:127.0.0.1:14600', wait_ready=True)
print get_ip()
print get_status(vehicle)
vehicle.close()