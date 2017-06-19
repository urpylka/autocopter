#!/usr/bin/env python
# -*- coding: utf8 -*-
# Import DroneKit-Python
from dronekit import VehicleMode, LocationGlobalRelative, LocationGlobal, Command, connect
import time, traceback, sys, math
from pymavlink import mavutil
from other_functions import get_ip
# ====================================================================================
# Устранение проблем с кодировкой UTF-8
# http://webhamster.ru/mytetrashare/index/mtb0/13566385393amcr1oegx
reload(sys)
sys.setdefaultencoding('utf8')
# ====================================================================================
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
class autocopterDronekit(object):
    def _new_state(self,CURRENT_STATE,NEW_STATE):
        self._stop_state = True
        self._old_state = CURRENT_STATE
        self._next_state = NEW_STATE
    def _create_mission(self,lat,lon):
        self._mission_created = False
        # exeption https://pythonworld.ru/tipy-dannyx-v-python/isklyucheniya-v-python-konstrukciya-try-except-dlya-obrabotki-isklyuchenij.html
        try:
            self._goto_location = LocationGlobalRelative(lat,lon,self._work_alt)
            # print 'Create a new mission (for current location)'
            self.adds_square_mission(self._vehicle.location.global_relative_frame, 6)
            self._mission_created = True
            return "Миссия успешно построена!"
        except Exception as ex:
            self._mission_created = False
            return "Произошла ошибка при построении миссии\n" + ex.message + "\n" + traceback.format_exc()
        finally:
            pass
    def get_location(self,bot,chat_id):
        bot.sendLocation(chat_id, self._vehicle.location.global_frame.latitude, self._vehicle.location.global_frame.longitude)
    def new_command(self,STATE,command,params=None):
        if STATE == 'INIT':
            return 'Ошибка 3! Некорректная команда %s' % command + ' для состояния %s' % STATE
        elif STATE == 'IDLE':
            if command == '/status':
                # вывод информации о коптере, ip, заряд батареи
                return "copter ip: %s" % get_ip() + \
                       "\nSTATE: %s" % STATE + \
                       "\n%s" % self.get_status
            elif command == 'create_mission':
                return self._create_mission(params['latitude'],params['longitude'])
            elif command == '/takeoff':
                self._new_state(STATE,'TAKEOFF')
                #return "Взлет из состояния: %s" % self._old_state
            else:
                return 'Ошибка 3! Некорректная команда ' + command + ' для состояния %s' % STATE
        elif STATE == 'TAKEOFF':
            if command == '/status':
                # вывод информации о коптере, ip, заряд батареи
                return "copter ip: " + get_ip() + '\n' + self.get_status + '\nSTATE: ' + STATE
            elif command == 'create_mission':
                return self._create_mission(params['latitude'], params['longitude'])
            elif command == '/land':
                self._new_state(STATE,'LAND')
                return "Посадка из состояния: %s" % self._old_state
            elif command == '/hover':
                self._new_state(STATE,'HOVER')
                return "Зависнуть из состояния: %s" % self._old_state
            else:
                return 'Ошибка 3! Некорректная команда ' + command + ' для состояния %s' % STATE
        elif STATE == 'HOVER':
            if command == '/status':
                # вывод информации о коптере, ip, заряд батареи
                return "copter ip: " + get_ip() + '\n' + self.get_status + '\nSTATE: ' + STATE
            elif command == '/stop':
                self.motors_off()
            elif command == 'create_mission':
                return self._create_mission(params['latitude'], params['longitude'])
            elif command == '/land':
                self._new_state(STATE,'LAND')
                return "Посадка из состояния: %s" % self._old_state
            elif command == '/rtl':
                self._new_state(STATE,'RTL')
                return "Возврат на точку взлета из состояния: %s" % self._old_state
            elif command == '/auto':
                self._new_state(STATE,'AUTO')
                return "Автопилот из состояния: %s" % self._old_state
            elif command == '/goto':
                self._new_state(STATE,'GOTO')
                return "Полет по координатам из состояния: %s" % self._old_state
            else:
                return 'Ошибка 3! Некорректная команда ' + command + ' для состояния %s' % STATE
        elif STATE == 'GOTO':
            if command == '/status':
                # вывод информации о коптере, ip, заряд батареи
                return "copter ip: " + get_ip() + '\n' + self.get_status + '\nSTATE: ' + STATE
            elif command == '/land':
                self._new_state(STATE,'LAND')
                return "Посадка из состояния: %s" % self._old_state
            elif command == '/rtl':
                self._new_state(STATE,'RTL')
                return "Возврат на точку взлета из состояния: %s" % self._old_state
            elif command == '/hover':
                self._new_state(STATE,'HOVER')
                return "Зависнуть из состояния: %s" % self._old_state
            else:
                return 'Ошибка 3! Некорректная команда ' + command + ' для состояния %s' % STATE
        elif STATE == 'LAND':
            if command == '/status':
                # вывод информации о коптере, ip, заряд батареи
                return "copter ip: " + get_ip() + '\n' + self.get_status + '\nSTATE: ' + STATE
            elif command == 'create_mission':
                return self._create_mission(params['latitude'], params['longitude'])
            elif command == '/hover':
                self._new_state(STATE,'HOVER')
                return "Зависнуть из состояния: %s" % self._old_state
            else:
                return 'Ошибка 3! Некорректная команда ' + command + ' для состояния ' + STATE
        elif STATE == 'AUTO':
            if command == '/status':
                # вывод информации о коптере, ip, заряд батареи
                return "copter ip: " + get_ip() + '\n' + self.get_status + '\nSTATE: ' + STATE + '\nРасстояние до следующего WP: ' + self.distance_to_current_waypoint + "м"
            elif command == '/land':
                self._new_state(STATE,'LAND')
                return "Посадка из состояния: %s" % self._old_state
            elif command == '/rtl':
                self._new_state(STATE,'RTL')
                return "Возврат на точку взлета из состояния: %s" % self._old_state
            elif command == '/hover':
                self._new_state(STATE,'HOVER')
                return "Зависнуть из состояния: %s" % self._old_state
            else:
                return 'Ошибка 3! Некорректная команда ' + command + ' для состояния ' + STATE
        elif STATE == 'RTL':
            if command == '/status':
                # вывод информации о коптере, ip, заряд батареи
                return "copter ip: " + get_ip() + '\n' + self.get_status() + '\nSTATE: ' + STATE
            elif command == '/land':
                self._new_state(STATE,'LAND')
                return "Посадка из состояния: %s" % self._old_state
            elif command == '/hover':
                self._new_state(STATE,'HOVER')
                return "Зависнуть из состояния: %s" % self._old_state
            else:
                return 'Ошибка 3! Некорректная команда ' + command + ' для состояния ' + STATE
        else:
            return 'Ошибка 4! Некорректное состояние ' + STATE
    def __init__(self,status_printer):
        # ==============================================================
        # построение миссии
        self._mission_created = False
        self._goto_location = None
        self._work_alt = 5
        # необходимость в HOVER
        self._need_hover = True
        # ==============================================================
        # Connect to the Vehicle (in this case a UDP endpoint)
        #проверка на подключается или нет
        #цикл пока не подключится?
        #http://python.dronekit.io/automodule.html#dronekit.connect
        # функция долгая (пишет через функцию status_printer)
        self._vehicle = None
        self._vehicle = connect('tcp:127.0.0.1:14600', wait_ready=True, status_printer=status_printer)
        # ==============================================================
        self._old_state = 'INIT'
        self._stop_state = False
        self._next_state = 'IDLE'
        # ==============================================================
    @property
    def status_of_connect(self):
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
        # Get some vehicle attributes (state)
        buf = "Get some vehicle attribute values:" + \
              "\nGPS: %s" % self._vehicle.gps_0 + \
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
    def distance_to_current_waypoint(self):
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
    def adds_square_mission(self, aLocation, aSize):
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
    def LAND(self, log_and_messages):
        self._old_state = 'LAND'
        log_and_messages.deb_pr_tel('STATE = ' + self._old_state)
        self._stop_state = False
        self._next_state = 'IDLE'
        # http://ardupilot.org/copter/docs/land-mode.html
        self._vehicle.mode = VehicleMode("LAND")
        while not self.onLand:
            if not self._stop_state:
                #log_and_messages.deb_pr_tel('Waiting for ' + self._old_state)
                time.sleep(1)
            else:
                log_and_messages.deb_pr_tel('Прерывание состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
                return self._next_state
        log_and_messages.deb_pr_tel('Успешное завершение состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
        return self._next_state
    def IDLE(self,log_and_messages):
        self._old_state = 'IDLE'
        log_and_messages.deb_pr_tel('STATE = ' + self._old_state)
        self._stop_state = False
        self._next_state = 'IDLE'
        # http://ardupilot.org/copter/docs/ac2_guidedmode.html
        # http://python.dronekit.io/examples/guided-set-speed-yaw-demo.html
        self._vehicle.armed = False
        self._vehicle.mode = VehicleMode("GUIDED")
        while True:
            if not self._stop_state:
                #log_and_messages.deb_pr_tel('I\'m in '+self._old_state)
                time.sleep(1)
            else:
                log_and_messages.deb_pr_tel(
                    'Прерывание состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
                return self._next_state
        log_and_messages.deb_pr_tel(
            'Успешное завершение состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
        return self._next_state
    def _simple_goto_wrapper(self,lat,lon,alt=20,groundspeed=7.5):
        # Задаем координаты нужной точки
        a_location = LocationGlobalRelative(lat,lon,alt)
        # полетели
        self._vehicle.simple_goto(a_location)
        # Путевая скорость, м/с
        self._vehicle.groundspeed = groundspeed
    def HOVER(self,log_and_messages):
        self._old_state = 'HOVER'
        log_and_messages.deb_pr_tel('STATE = ' + self._old_state)
        self._stop_state = False
        self._next_state = 'HOVER'
        self._vehicle.mode = VehicleMode("GUIDED")
        if self._need_hover:
            self._simple_goto_wrapper(self._vehicle.location.global_relative_frame.lat,self._vehicle.location.global_relative_frame.lon,self._vehicle.location.global_relative_frame.alt)
        self._need_hover = True #сброс
        while True:
            if not self._stop_state:
                #log_and_messages.deb_pr_tel('I\'m in '+self._old_state)
                time.sleep(1)
            else:
                log_and_messages.deb_pr_tel(
                    'Прерывание состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
                return self._next_state
        log_and_messages.deb_pr_tel(
            'Успешное завершение состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
        return self._next_state
    def RTL(self,log_and_messages):
        self._old_state = 'RTL'
        log_and_messages.deb_pr_tel('STATE = ' + self._old_state)
        self._stop_state = False
        self._next_state = 'IDLE'
        # http://ardupilot.org/copter/docs/rtl-mode.html
        self._vehicle.mode = VehicleMode("RTL")
        while not self.onLand:
            if not self._stop_state:
                #log_and_messages.deb_pr_tel('Waiting for ' + self._old_state)
                time.sleep(1)
            else:
                log_and_messages.deb_pr_tel(
                    'Прерывание состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
                return self._next_state
        log_and_messages.deb_pr_tel(
            'Успешное завершение состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
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
    def TAKEOFF(self, log_and_messages):
        aTargetAltitude = self._work_alt
        self._old_state = 'TAKEOFF'
        log_and_messages.deb_pr_tel('STATE = ' + self._old_state)
        self._stop_state = False
        self._next_state = 'HOVER'
        """
        Arms vehicle and fly to aTargetAltitude.
        """
        log_and_messages.deb_pr_tel('Basic pre-arm checks')
        # Don't let the user try to arm until autopilot is ready
        log_and_messages.deb_pr_tel('Waiting for vehicle to initialise...')
        while not self._is_armable: #проверка не дронкита, а собственная
            if not self._stop_state:
                #log_and_messages.deb_pr_tel('Waiting for ' + self._old_state)
                #log_and_messages.deb_pr_tel('Waiting for vehicle to initialise...')
                time.sleep(1)
            else:
                log_and_messages.deb_pr_tel(
                    'Прерывание состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
                log_and_messages.deb_pr_tel('Stopping takeoff on pre-arm!')
                return self._next_state
        # Copter should arm in GUIDED mode
        self._vehicle.mode = VehicleMode("GUIDED")
        log_and_messages.deb_pr_tel('Arming motors')
        self._vehicle.armed = True
        while not self._vehicle.armed:
            if not self._stop_state:
                #log_and_messages.deb_pr_tel('Waiting for ' + self._old_state)
                #log_and_messages.deb_pr_tel('Waiting for arming...')
                time.sleep(1)
            else:
                log_and_messages.deb_pr_tel(
                    'Прерывание состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
                log_and_messages.deb_pr_tel('Stopping takeoff on arm!')
                return self._next_state
        log_and_messages.deb_pr_tel('Taking off!')
        self._vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude
        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after Vehicle.simple_takeoff will execute immediately).
        while self._vehicle.location.global_relative_frame.alt < aTargetAltitude * 0.95: # Trigger just below target alt.
            if not self._stop_state:
                #log_and_messages.deb_pr_tel('Waiting for ' + self._old_state)
                log_and_messages.deb_pr_tel("Altitude: %s" % self._vehicle.location.global_relative_frame.alt)
                time.sleep(1)
            else:
                log_and_messages.deb_pr_tel(
                    'Прерывание состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
                log_and_messages.deb_pr_tel('Stopping takeoff on fly!')
                return self._next_state
        log_and_messages.deb_pr_tel(
            'Успешное завершение состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
        self._need_hover = False
        return self._next_state
    def _is_arrived(self, lat, lon, alt, precision=0.3):
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
    def GOTO(self,log_and_messages):
        self._next_state = self._old_state # должен быть только HOVER
        if self._mission_created:
            self._old_state = 'GOTO'
            log_and_messages.deb_pr_tel('STATE = ' + self._old_state)
            self._stop_state = False
            self._next_state = 'HOVER'
            self._vehicle.mode = VehicleMode("GUIDED")
            self._simple_goto_wrapper(self._goto_location.lat,self._goto_location.lon,self._goto_location.alt)
            while self._is_arrived(self._goto_location.lat,self._goto_location.lon,self._goto_location.alt):
                if not self._stop_state:
                    #log_and_messages.deb_pr_tel('I\'m in '+self._old_state)
                    log_and_messages.deb_pr_tel('До точки назначения: ' + get_distance_metres(self._goto_location, self._vehicle.location.global_relative_frame) + "м")
                    time.sleep(1)
                else:
                    log_and_messages.deb_pr_tel(
                        'Прерывание состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
                    return self._next_state
            log_and_messages.deb_pr_tel(
                'Успешное завершение состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
            self._need_hover = False
            return self._next_state
        else:
            log_and_messages.deb_pr_tel(
                'Ошибка: Создайте миссию заранее! Сейчас ' + self._old_state + ' переключение в состояние ' + self._next_state)
            return self._next_state
    def AUTO(self, log_and_messages):
        self._next_state = self._old_state  # должен быть только HOVER
        if self._mission_created:
            self._old_state = 'AUTO'
            log_and_messages.deb_pr_tel('STATE = ' + self._old_state)
            self._stop_state = False
            self._next_state = 'HOVER'
            log_and_messages.deb_pr_tel("Starting mission")
            # Reset mission set to first (0) waypoint
            self._vehicle.commands.next = 0

            # Set mode to AUTO to start mission
            # http://ardupilot.org/copter/docs/auto-mode.html
            self._vehicle.mode = VehicleMode("AUTO")

            # Monitor mission.
            # Demonstrates getting and setting the command number
            # Uses distance_to_current_waypoint(), a convenience function for finding the
            #   distance to the next waypoint.

            while True:
                if not self._stop_state:
                    nextwaypoint = self._vehicle.commands.next
                    log_and_messages.deb_pr_tel('Distance to waypoint (%s): %sм' % (nextwaypoint, self.distance_to_current_waypoint))
                    time.sleep(1)
                else:
                    log_and_messages.deb_pr_tel(
                        'Прерывание состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
                    return self._next_state
            log_and_messages.deb_pr_tel(
                'Успешное завершение состояния ' + self._old_state + ' переключение в состояние ' + self._next_state)
            # может и не нужна стабилизация но на всякий (вдруг failsafe будет)
            # self._need_hover = False
            return self._next_state
        else:
            log_and_messages.deb_pr_tel(
                'Ошибка: Создайте миссию заранее! Сейчас ' + self._old_state + ' переключение в состояние ' + self._next_state)
            return self._next_state
    def motors_off(self):
        msg = self._vehicle.message_factory.command_long_encode(
            0, 0,  # target system, target component
            mavutil.mavlink.MAV_CMD_DO_FLIGHTTERMINATION,  # command
            0,  # confirmation
            1,  # Flight termination activated if > 0.5
            0, 0, 0, 0, 0, 0)
        self._vehicle.send_mavlink(msg)