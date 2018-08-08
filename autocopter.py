#!/usr/bin/env python
# -*- coding: utf8 -*-

import time, traceback, sys, math, socket
from enum import Enum
import telepot
import http.client
from pymavlink import mavutil
from dronekit import VehicleMode, LocationGlobalRelative, LocationGlobal, Command, connect
from telegrambot import TelegramBot
# ====================================================================================
# Устранение проблем с кодировкой UTF-8
# http://webhamster.ru/mytetrashare/index/mtb0/13566385393amcr1oegx
reload(sys)
sys.setdefaultencoding('utf8')
# ====================================================================================

class States(Enum):
    """
    States of drone
    """
    INIT = 1
    IDLE = 2
    TAKEOFF = 3
    HOVER = 4
    RTL = 5
    AUTO = 6
    LAND = 7
    GOTO = 8

def check_internet():
    try:
        socket.gethostbyaddr('ya.ru')
    except socket.gaierror:
        return False
    return True

def wait_internet():
    while not check_internet():
        time.sleep(1)

def get_ip():
    #conn = http.client.HTTPConnection("smirart.ru")
    #conn.request("GET", "/ip")
    #return conn.getresponse().read()
    return "FIX_IP"

def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the
    specified `original_location`. The returned Location has the same `alt` value
    as `original_location`.

    The function is useful when you want to move the vehicle around specifying locations relative to
    the current vehicle position.
    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius = 6378137.0  # Radius of "spherical" earth
    # Coordinate offsets in radians
    dLat = dNorth / earth_radius
    dLon = dEast / (earth_radius * math.cos(math.pi * original_location.lat / 180))

    # New position in decimal degrees
    newlat = original_location.lat + (dLat * 180 / math.pi)
    newlon = original_location.lon + (dLon * 180 / math.pi)
    return LocationGlobal(newlat, newlon, original_location.alt)

def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5

class Autocopter(object):
    """
    This class consists of logic for states (methods 'do_*' & dependencies) and method 'new_command'
    """
    def __init__(self, token, chat_id, debug = True):
        self._vehicle = None

        # Params of info-messages
        self.bot = TelegramBot(token, chat_id, debug, self)
        self.debug_message = self.bot.debug_message

        # Params of auto-missions
        self._mission_created = False
        self._goto_location = None
        self._work_alt = 20
        self._need_hover = True

        # Params of states machine
        self.current_state = States.INIT
        self._stop_state = False
        self._next_state = States.IDLE

    def _create_mission(self, lat, lon):
        self._mission_created = False
        # exeption https://pythonworld.ru/tipy-dannyx-v-python/isklyucheniya-v-python-konstrukciya-try-except-dlya-obrabotki-isklyuchenij.html
        try:
            self._goto_location = LocationGlobalRelative(lat, lon, self._work_alt)
            # print 'Create a new mission (for current location)'
            self._adds_square_mission(self._vehicle.location.global_relative_frame, 6)
            self._mission_created = True
            return "Миссия успешно построена!"
        except Exception as ex:
            self._mission_created = False
            return "Произошла ошибка при построении миссии\n" + ex.message + "\n" + traceback.format_exc()
        finally:
            pass

    def new_state(self, new_state):
        self._stop_state = True
        self._next_state = new_state

    @property
    def get_location():
        return self._vehicle.location.global_frame.lat, self._vehicle.location.global_frame.lon
    
    @property
    def _status_of_connect(self):
        if self._vehicle != None:
            return True
        else:
            raise Exception("Не удалось подключиться к APM")

    def disconnect(self):
        '''
        Close vehicle object before exiting script
        :return:
        '''
        if self._vehicle != None:
            self._vehicle.close()

    @property
    def get_status(self):
        buf = "\nGPS: %s" % self._vehicle.gps_0 + \
              "\nBattery: %s" % self._vehicle.battery + \
              "\nLast Heartbeat: %s" % self._vehicle.last_heartbeat + \
              "\nIs Armable?: %s" % self._is_armable + \
              "\nSystem status: %s" % self._vehicle.system_status.state + \
              "\nMode: %s" % self._vehicle.mode.name + \
              "\nGlobal Location: %s" % self._vehicle.location.global_frame + \
              "\nGlobal Relative Location: %s" % self._vehicle.location.global_relative_frame + \
              "\nLocal Location: %s" % self._vehicle.location.local_frame + \
              "\nAttitude: %s" % self._vehicle.attitude + \
              "\nHeading: %s" % self._vehicle.heading + \
              "\nGroundspeed: %s" % self._vehicle.groundspeed + \
              "\nAirspeed: %s" % self._vehicle.airspeed
        return buf

    @property
    def _distance_to_current_waypoint(self):
        """
        Gets distance in metres to the current waypoint.
        It returns None for the first waypoint (Home location).
        """
        nextwaypoint = self._vehicle.commands.next
        if nextwaypoint == 0:
            return None
        missionitem = self._vehicle.commands[nextwaypoint - 1]  # commands are zero indexed
        lat = missionitem.x
        lon = missionitem.y
        alt = missionitem.z
        targetWaypointLocation = LocationGlobalRelative(lat, lon, alt)
        distancetopoint = get_distance_metres(self._vehicle.location.global_frame, targetWaypointLocation)
        return distancetopoint

    def download_mission(self):
        """
        Download the current mission from the vehicle.
        """
        cmds = self._vehicle.commands
        cmds.download()
        cmds.wait_ready()  # wait until download is complete.

    def _adds_square_mission(self, aLocation, aSize):
        """
        Adds a takeoff command and four waypoint commands to the current mission.
        The waypoints are positioned to form a square of side length 2*aSize around the specified LocationGlobal (aLocation).

        The function assumes vehicle.commands matches the vehicle mission state
        (you must have called download at least once in the session and after clearing the mission)
        """
        cmds = self._vehicle.commands
        print "Clear any existing commands"
        cmds.clear()
        print "Define/add new commands."
        # Add new commands. The meaning/order of the parameters is documented in the Command class.

        # Add MAV_CMD_NAV_TAKEOFF command. This is ignored if the vehicle is already in the air.
        cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0,
                    0, 0, 0, 0, 10))
        # Define the four MAV_CMD_NAV_WAYPOINT locations and add the commands
        point1 = get_location_metres(aLocation, aSize, -aSize)
        point2 = get_location_metres(aLocation, aSize, aSize)
        point3 = get_location_metres(aLocation, -aSize, aSize)
        point4 = get_location_metres(aLocation, -aSize, -aSize)
        cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0,
                    0, 0, 0, point1.lat, point1.lon, 11))
        cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0,
                    0, 0, 0, point2.lat, point2.lon, 12))
        cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0,
                    0, 0, 0, point3.lat, point3.lon, 13))
        cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0,
                    0, 0, 0, point4.lat, point4.lon, 14))
        # add dummy waypoint "5" at point 4 (lets us know when have reached destination)
        cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0,
                    0, 0, 0, point4.lat, point4.lon, 14))
        print "Upload new commands to vehicle"
        cmds.upload()

    @property
    def onLand(self):
        return self._vehicle.system_status.state == 'STANDBY'

    def do_INIT(self):
        self.current_state = States.INIT

        wait_internet()
        self.debug_message("Autocopter is online: %s" % get_ip())

        self.debug_message("STATE = %s" % self.current_state)

        self.bot.start_handler()
        time.sleep(1.5)  # время на ответ сообщений пришедших в выключенный период

        while True:
            try:
                self.debug_message("Connecting to APM ...")
                # http://python.dronekit.io/automodule.html#dronekit.connect
                # функция долгая (пишет через функцию status_printer)
                self._vehicle = connect('tcp:127.0.0.1:14600', wait_ready = True, status_printer = self.debug_message)

                if self._status_of_connect:
                    self.debug_message("Connect successful!")
                    next_state = States.IDLE
                    self.debug_message("Успешное завершение состояния %s" % self.current_state + " переключение в состояние %s" % next_state)
                    self.current_state = next_state
                    break

            except Exception as ex:
                #self.debug_message("Ошибка в состоянии %s" % self.current_state + ":\n" + ex.message + "\n" + traceback.format_exc() + "\n")
                self.debug_message("Connection failed!")
                self.debug_message("Timeout 10s")
                time.sleep(10)

    def do_LAND(self):
        self.current_state = States.LAND
        self.debug_message('STATE = ' + self.current_state)
        self._stop_state = False
        self._next_state = States.IDLE
        # http://ardupilot.org/copter/docs/land-mode.html
        self._vehicle.mode = VehicleMode("LAND")
        while not self.onLand:
            if not self._stop_state:
                #self.debug_message('Waiting for ' + self.current_state)
                time.sleep(1)
            else:
                self.debug_message("Прерывание состояния " + self.current_state + " переключение в состояние " + self._next_state)
                return self._next_state
        self.debug_message("Успешное завершение состояния " + self.current_state + " переключение в состояние " + self._next_state)
        return self._next_state

    def do_IDLE(self):
        self.current_state = States.IDLE
        self.debug_message("STATE = %s" % self.current_state)
        self._stop_state = False
        self._next_state = States.IDLE
        # http://ardupilot.org/copter/docs/ac2_guidedmode.html
        # http://python.dronekit.io/examples/guided-set-speed-yaw-demo.html
        self._vehicle.armed = False
        self._vehicle.mode = VehicleMode("GUIDED")
        while True:
            if not self._stop_state:
                #self.debug_message('I\'m in '+self.current_state)
                time.sleep(1)
            else:
                self.debug_message("Прерывание состояния " + self.current_state + " переключение в состояние " + self._next_state)
                return self._next_state
        self.debug_message("Успешное завершение состояния " + self.current_state + " переключение в состояние " + self._next_state)
        return self._next_state

    def _simple_goto_wrapper(self, lat, lon, alt = 20, groundspeed = 7.5):
        # Задаем координаты нужной точки
        a_location = LocationGlobalRelative(lat,lon,alt)
        # полетели
        self._vehicle.simple_goto(a_location)
        # Путевая скорость, м/с
        self._vehicle.groundspeed = groundspeed

    def do_HOVER(self):
        self.current_state = States.HOVER
        self.debug_message("STATE = %s" % self.current_state)
        self._stop_state = False
        self._next_state = States.HOVER
        self._vehicle.mode = VehicleMode("GUIDED")
        if self._need_hover:
            self._simple_goto_wrapper(self._vehicle.location.global_relative_frame.lat, self._vehicle.location.global_relative_frame.lon, self._vehicle.location.global_relative_frame.alt)
        self._need_hover = True #сброс
        while True:
            if not self._stop_state:
                #self.debug_message('I\'m in '+self.current_state)
                time.sleep(1)
            else:
                self.debug_message("Прерывание состояния " + self.current_state + " переключение в состояние " + self._next_state)
                return self._next_state
        self.debug_message("Успешное завершение состояния " + self.current_state + " переключение в состояние " + self._next_state)
        return self._next_state

    def do_RTL(self):
        self.current_state = 'RTL'
        self.debug_message("STATE = %s" % self.current_state)
        self._stop_state = False
        self._next_state = States.IDLE
        # http://ardupilot.org/copter/docs/rtl-mode.html
        self._vehicle.mode = VehicleMode("RTL")
        while not self.onLand:
            if not self._stop_state:
                #self.debug_message('Waiting for ' + self.current_state)
                time.sleep(1)
            else:
                self.debug_message("Прерывание состояния " + self.current_state + " переключение в состояние " + self._next_state)
                return self._next_state
        self.debug_message("Успешное завершение состояния " + self.current_state + " переключение в состояние " + self._next_state)
        return self._next_state

    @property
    def _is_armable(self):
        """
        Returns `True` if the vehicle is ready to arm, false otherwise (``Boolean``).

        This attribute wraps a number of pre-arm checks, ensuring that the vehicle has booted,
        has a good GPS fix, and that the EKF pre-arm is complete.
        """
        # check that mode is not INITIALSING
        # check that we have a GPS fix
        # check that EKF pre-arm is complete
        return self._vehicle.mode != 'INITIALISING' and self._vehicle.gps_0.fix_type > 1# and self.vehicle._ekf_predposhorizabs #отключена проверка ekf

    def do_TAKEOFF(self):
        aTargetAltitude = self._work_alt
        self.current_state = States.TAKEOFF
        self.debug_message("STATE = %s" % self.current_state)
        self._stop_state = False
        self._next_state = States.GOTO
        """
        Arms vehicle and fly to aTargetAltitude.
        """
        self.debug_message("Basic pre-arm checks")
        # Don't let the user try to arm until autopilot is ready
        self.debug_message("Waiting for vehicle to initialise...")
        while not self._is_armable: #проверка не дронкита, а собственная
            if not self._stop_state:
                #self.debug_message('Waiting for ' + self.current_state)
                #self.debug_message('Waiting for vehicle to initialise...')
                time.sleep(1)
            else:
                self.debug_message("Прерывание состояния " + self.current_state + " переключение в состояние " + self._next_state)
                self.debug_message("Stopping takeoff on pre-arm!")
                return self._next_state
        # Copter should arm in GUIDED mode
        self._vehicle.mode = VehicleMode("GUIDED")
        self.debug_message("Arming motors")
        self._vehicle.armed = True
        while not self._vehicle.armed:
            if not self._stop_state:
                #self.debug_message('Waiting for ' + self.current_state)
                #self.debug_message('Waiting for arming...')
                time.sleep(1)
            else:
                self.debug_message("Прерывание состояния " + self.current_state + " переключение в состояние " + self._next_state)
                self.debug_message("Stopping takeoff on arm!")
                return self._next_state
        self.debug_message("Taking off!")
        self._vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude
        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after Vehicle.simple_takeoff will execute immediately).
        while self._vehicle.location.global_relative_frame.alt < aTargetAltitude * 0.95: # Trigger just below target alt.
            if not self._stop_state:
                #self.debug_message('Waiting for ' + self.current_state)
                self.debug_message("Altitude: %s" % self._vehicle.location.global_relative_frame.alt)
                time.sleep(1)
            else:
                self.debug_message("Прерывание состояния " + self.current_state + " переключение в состояние " + self._next_state)
                self.debug_message("Stopping takeoff on fly!")
                return self._next_state
        self.debug_message("Успешное завершение состояния " + self.current_state + " переключение в состояние " + self._next_state)
        self._need_hover = False
        return self._next_state

    def _is_arrived(self, lat, lon, alt, precision = 0.3):
        # функция взята из https://habrahabr.ru/post/281591/
        # текущая позиция
        veh_loc = self._vehicle.location.global_relative_frame
        # получаем данные в метрах
        diff_lat_m = (lat - veh_loc.lat) * 1.113195e5
        diff_lon_m = (lon - veh_loc.lon) * 1.113195e5
        diff_alt_m = alt - veh_loc.alt
        # отклонение
        dist_xyz = math.sqrt(diff_lat_m ** 2 + diff_lon_m ** 2 + diff_alt_m ** 2)
        if dist_xyz < precision:
            #print "Прибыли на место"
            return True
        else:
            #print "Еще не долетели"
            return False

    def do_GOTO(self):
        self._next_state = States.HOVER # должен быть только HOVER
        if self._mission_created:
            self.current_state = States.GOTO
            self.debug_message("STATE = %s" % self.current_state)
            self._stop_state = False
            self._next_state = States.HOVER
            self._vehicle.mode = VehicleMode("GUIDED")
            self._simple_goto_wrapper(self._goto_location.lat, self._goto_location.lon, self._goto_location.alt)
            while self._is_arrived(self._goto_location.lat, self._goto_location.lon, self._goto_location.alt):
                if not self._stop_state:
                    #self.debug_message('I\'m in '+self.current_state)
                    self.debug_message("До точки назначения: " + get_distance_metres(self._goto_location, self._vehicle.location.global_relative_frame) + "м")
                    time.sleep(1)
                else:
                    self.debug_message("Прерывание состояния " + self.current_state + " переключение в состояние " + self._next_state)
                    return self._next_state
            self.debug_message("Успешное завершение состояния " + self.current_state + " переключение в состояние " + self._next_state)
            self._need_hover = False
            return self._next_state
        else:
            self.debug_message("Ошибка: Создайте миссию заранее! Сейчас " + self.current_state + " переключение в состояние " + self._next_state)
            return self._next_state

    def do_AUTO(self):
        self._next_state = self.current_state  # должен быть только HOVER
        if self._mission_created:
            self.current_state = States.AUTO
            self.debug_message("STATE = %s" % self.current_state)
            self._stop_state = False
            self._next_state = States.HOVER
            self.debug_message("Starting mission")
            # Reset mission set to first (0) waypoint
            self._vehicle.commands.next = 0

            # Set mode to AUTO to start mission
            # http://ardupilot.org/copter/docs/auto-mode.html
            self._vehicle.mode = VehicleMode("AUTO")

            # Monitor mission.
            # Demonstrates getting and setting the command number
            # Uses _distance_to_current_waypoint(), a convenience function for finding the
            #   distance to the next waypoint.

            while True:
                if not self._stop_state:
                    nextwaypoint = self._vehicle.commands.next
                    self.debug_message("Distance to waypoint (%s): %sм" % (nextwaypoint, self._distance_to_current_waypoint))
                    time.sleep(1)
                else:
                    self.debug_message("Прерывание состояния " + self.current_state + " переключение в состояние " + self._next_state)
                    return self._next_state
            self.debug_message("Успешное завершение состояния " + self.current_state + " переключение в состояние " + self._next_state)
            # может и не нужна стабилизация но на всякий (вдруг failsafe будет)
            # self._need_hover = False
            return self._next_state
        else:
            self.debug_message("Ошибка: Создайте миссию заранее! Сейчас " + self.current_state + " переключение в состояние " + self._next_state)
            return self._next_state

def main():
    autocopter = None
    try:
        autocopter = Autocopter(TOKEN, MY_CHAT_ID, DEBUG)
        while True:
            try:
                if autocopter.current_state == States.INIT:
                    autocopter.do_INIT()
                elif autocopter.current_state == States.IDLE:
                    autocopter.do_IDLE()
                elif autocopter.current_state == States.TAKEOFF:
                    autocopter.do_TAKEOFF()
                elif autocopter.current_state == States.HOVER:
                    autocopter.do_HOVER()
                elif autocopter.current_state == States.RTL:
                    autocopter.do_RTL()
                elif autocopter.current_state == States.AUTO:
                    autocopter.do_AUTO()
                elif autocopter.current_state == States.LAND:
                    autocopter.do_LAND()
                elif autocopter.current_state == States.GOTO:
                    autocopter.do_GOTO()
            except Exception as ex:
                autocopter.debug_message("Ошибка в состоянии %s" % autocopter.current_state + ":\n" + ex.message + "\n" + traceback.format_exc() + "\n")
    finally:
        if autocopter != None: autocopter.disconnect()
        print "\n######################################################"
        print "\nDisconnect APM\n"
        print "######################################################\n"

if __name__ == "__main__":
    DEBUG = True
    TOKEN = sys.argv[1]
    MY_CHAT_ID = sys.argv[2]
    main()
