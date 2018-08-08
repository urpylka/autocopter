#!/usr/bin/python
# -*- coding: utf8 -*-

from dronekit import connect

def get_status(_vehicle):
    """
    Get some vehicle atribute values
    """
    buf = "\nGPS: %s" % _vehicle.gps_0 + \
          "\nBattery: %s" % _vehicle.battery + \
          "\nLast Heartbeat: %s" % _vehicle.last_heartbeat + \
          "\nIs Armable?: %s" % vehicle._is_armable + \
          "\nSystem status: %s" % _vehicle.system_status.state + \
          "\nMode: %s" % _vehicle.mode.name
    return buf

vehicle = connect('tcp:127.0.0.1:14600', wait_ready=True)
print get_status(vehicle)
vehicle.close()
