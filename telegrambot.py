#!/usr/bin/env python
# -*- coding: utf8 -*-

import time
import traceback
import telepot
from telepot.loop import MessageLoop

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class TelegramBot(object):
    """
    Здесь находится метод для создания отладочных сообщений,
    а также здесь крутиться в отдельном потоке метод обработки
    пользовательских сообщений
    """

    def __init__(self, _token, _chat_id, _debug, _autocopter):
        self.bot = telepot.Bot(_token)
        self.chat_id = _chat_id
        self.debug = _debug
        self.autocopter = _autocopter
        telepot.api.set_proxy('http://200.172.103.227:20183')

    def debug_message(self, msg):
        if self.debug:
            try:
                print msg
                self.bot.sendMessage(self.chat_id, msg)
            except Exception as ex:
                print "Произошла ошибка при отправке сообщения:\n" + ex.message + "\n" + traceback.format_exc()

    def start_handler(self):
        MessageLoop(self.bot, self.handle).run_as_thread()

    def handle(self, msg):
            """
            хендлер выполняется в отдельном потоке,
            вызывается событием на подобие блокирующей очереди
            """
            content_type, chat_type, chat_id = telepot.glance(msg)
            if self.debug:
                print(content_type, chat_type, chat_id)
            if chat_id == self.chat_id:
                if content_type == 'text':
                    self.debug_message(self.new_command(msg['text']))
                elif content_type == 'location':
                    self.debug_message(self.new_command('create_mission', msg['location']))
                elif content_type == 'sticker':
                    self.new_command('get_location')
                else:
                    self.debug_message("Ошибка 2! Неверный тип: только text и location")
            else:
                self.debug_message("Ошибка 1! Access error!")

    def new_command(self, command, params = None):
            if self.autocopter.current_state == States.INIT:
                return "Ошибка 3! Некорректная команда %s" % command + " для состояния %s" % self.autocopter.current_state

            elif self.autocopter.current_state == States.IDLE:
                if command == '/status':
                    # вывод информации о коптере, ip, заряд батареи
                    return "copter ip: %s" % get_ip() + \
                        "\nSTATE: %s" % self.autocopter.current_state + \
                        "\n%s" % self.autocopter.get_status
                elif command == 'create_mission':
                    self.autocopter.new_state(States.TAKEOFF)
                    return self.autocopter.create_mission(params['latitude'], params['longitude'])
                elif command == '/takeoff':
                    self.autocopter.new_state(States.TAKEOFF)
                    #return "Взлет из состояния: %s" % self.autocopter.current_state
                elif command == 'get_location':
                    lat, lon = self.autocopter.get_location()
                    self.bot.sendLocation(self.chat_id, lat, lon)
                else:
                    return 'Ошибка 3! Некорректная команда ' + command + " для состояния %s" % self.autocopter.current_state

            elif self.autocopter.current_state == States.TAKEOFF:
                if command == '/status':
                    # вывод информации о коптере, ip, заряд батареи
                    return "copter ip: " + get_ip() + "\n" + self.autocopter.get_status + "\nSTATE: %s" % self.autocopter.current_state
                elif command == 'create_mission':
                    return self.autocopter.create_mission(params['latitude'], params['longitude'])
                elif command == '/land':
                    self.autocopter.new_state(States.LAND)
                    return "Посадка из состояния: %s" % self.autocopter.current_state
                elif command == '/hover':
                    self.autocopter.new_state(States.HOVER)
                    return "Зависнуть из состояния: %s" % self.autocopter.current_state
                elif command == 'get_location':
                    lat, lon = self.autocopter.get_location()
                    self.bot.sendLocation(self.chat_id, lat, lon)
                else:
                    return "Ошибка 3! Некорректная команда " + command + " для состояния %s" % self.autocopter.current_state

            elif self.autocopter.current_state == States.HOVER:
                if command == '/status':
                    # вывод информации о коптере, ip, заряд батареи
                    return "copter ip: " + get_ip() + "\n" + self.autocopter.get_status + "\nSTATE: %s" % self.autocopter.current_state
                elif command == 'create_mission':
                    return self.autocopter.create_mission(params['latitude'], params['longitude'])
                elif command == '/land':
                    self.autocopter.new_state(States.LAND)
                    return "Посадка из состояния: %s" % self.autocopter.current_state
                elif command == '/rtl':
                    self.autocopter.new_state('RTL')
                    return "Возврат на точку взлета из состояния: %s" % self.autocopter.current_state
                elif command == '/auto':
                    self.autocopter.new_state(States.AUTO)
                    return "Автопилот из состояния: %s" % self.autocopter.current_state
                elif command == '/goto':
                    self.autocopter.new_state(States.GOTO)
                    return "Полет по координатам из состояния: %s" % self.autocopter.current_state
                elif command == 'get_location':
                    lat, lon = self.autocopter.get_location()
                    self.bot.sendLocation(self.chat_id, lat, lon)
                else:
                    return "Ошибка 3! Некорректная команда " + command + " для состояния %s" % self.autocopter.current_state

            elif self.autocopter.current_state == States.GOTO:
                if command == '/status':
                    # вывод информации о коптере, ip, заряд батареи
                    return "copter ip: " + get_ip() + "\n" + self.autocopter.get_status + "\nSTATE: %s" % self.autocopter.current_state
                elif command == '/land':
                    self.autocopter.new_state(States.LAND)
                    return "Посадка из состояния: %s" % self.autocopter.current_state
                elif command == '/rtl':
                    self.autocopter.new_state('RTL')
                    return "Возврат на точку взлета из состояния: %s" % self.autocopter.current_state
                elif command == '/hover':
                    self.autocopter.new_state(States.HOVER)
                    return "Зависнуть из состояния: %s" % self.autocopter.current_state
                elif command == 'get_location':
                    lat, lon = self.autocopter.get_location()
                    self.bot.sendLocation(self.chat_id, lat, lon)
                else:
                    return 'Ошибка 3! Некорректная команда ' + command + " для состояния %s" % self.autocopter.current_state

            elif self.autocopter.current_state == States.LAND:
                if command == '/status':
                    # вывод информации о коптере, ip, заряд батареи
                    return "copter ip: " + get_ip() + "\n" + self.autocopter.get_status + "\nSTATE: %s" % self.autocopter.current_state
                elif command == 'create_mission':
                    return self.autocopter.create_mission(params['latitude'], params['longitude'])
                elif command == '/hover':
                    self.autocopter.new_state(States.HOVER)
                    return "Зависнуть из состояния: %s" % self.autocopter.current_state
                elif command == 'get_location':
                    lat, lon = self.autocopter.get_location()
                    self.bot.sendLocation(self.chat_id, lat, lon)
                else:
                    return 'Ошибка 3! Некорректная команда ' + command + " для состояния %s" % self.autocopter.current_state

            elif self.autocopter.current_state == States.AUTO:
                if command == '/status':
                    # вывод информации о коптере, ip, заряд батареи
                    return "copter ip: " + get_ip() + "\n" + self.autocopter.get_status + "\nSTATE: %s" % self.autocopter.current_state + '\nРасстояние до следующего WP: ' + self.distance_to_current_waypoint + "м"
                elif command == '/land':
                    self.autocopter.new_state(States.LAND)
                    return "Посадка из состояния: %s" % self.autocopter.current_state
                elif command == '/rtl':
                    self.autocopter.new_state('RTL')
                    return "Возврат на точку взлета из состояния: %s" % self.autocopter.current_state
                elif command == '/hover':
                    self.autocopter.new_state(States.HOVER)
                    return "Зависнуть из состояния: %s" % self.autocopter.current_state
                elif command == 'get_location':
                    lat, lon = self.autocopter.get_location() 
                    self.bot.sendLocation(self.chat_id, lat, lon)
                else:
                    return 'Ошибка 3! Некорректная команда ' + command + " для состояния %s" % self.autocopter.current_state

            elif self.autocopter.current_state == States.RTL:
                if command == '/status':
                    # вывод информации о коптере, ip, заряд батареи
                    return "copter ip: " + get_ip() + "\n" + self.autocopter.get_status + "\nSTATE: %s" % self.autocopter.current_state
                elif command == '/land':
                    self.autocopter.new_state(States.LAND)
                    return "Посадка из состояния: %s" % self.autocopter.current_state
                elif command == '/hover':
                    self.autocopter.new_state(States.HOVER)
                    return "Зависнуть из состояния: %s" % self.autocopter.current_state
                elif command == 'get_location':
                    lat, lon = self.autocopter.get_location()
                    self.bot.sendLocation(self.chat_id, lat, lon)
                else:
                    return "Ошибка 3! Некорректная команда " + command + " для состояния " + self.autocopter.current_state

            else:
                return "Ошибка 4! Нет обработчика для состояния: " + self.autocopter.current_state

if __name__ == "__main__":
    from autocopter import States
    class Autocopter(object):
        def __init__(self):
            self.current_state = States.IDLE
        def get_location(self):
            return 53, 50
    autocopter = Autocopter()
    bot = TelegramBot("326953186:AAHGxltq7oYvgfJXh0_76O96pGIpeKr8x-Q", 62922848, True, autocopter)
    bot.start_handler()
    bot.debug_message("Listening...")
    while 1:
        time.sleep(10)