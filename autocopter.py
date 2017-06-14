#!/usr/bin/env python
# -*- coding: utf8 -*-
DEBUG = True

# Устранение проблем с кодировкой UTF-8
# http://webhamster.ru/mytetrashare/index/mtb0/13566385393amcr1oegx
import sys
reload(sys)
sys.setdefaultencoding('utf8')

STATE = 'INIT'
try:
    while 1:
        if STATE == 'INIT':
            # ==========================================================================================================
            # блокировка до тех пор, пока не будет соединения с интернетом
            from other_functions import wait_internet
            wait_internet()
            # ===========================================================================================================
            # START TELEGRAM BOT
            import sys, telepot
            TOKEN = sys.argv[1]  # get token from command-line
            bot = telepot.Bot(TOKEN)
            # ==========================================================================================================
            from other_functions import get_ip
            bot.sendMessage(62922848, "Autocopter is online: %s" % get_ip())

            def handle(msg):
                """хендлер выполняется в отдельном потоке, вызывается событием на подобие блокирующей очереди"""
                content_type, chat_type, chat_id = telepot.glance(msg)
                print(content_type, chat_type, chat_id)
                if chat_id == 62922848:
                    # global STATE #https://foxford.ru/wiki/informatika/oblasti-vidimosti-peremennyh-v-python#!
                    if STATE != 'INIT':
                        if content_type == 'text':
                            if msg['text'] == '/start':
                                # попытка совершения полета в указанную точку в режиме APM AUTO
                                bot.sendMessage(chat_id, 'try starting mission...')
                            elif msg['text'] == '/status':
                                # вывод информации о коптере, ip, заряд батареи
                                # bot.sendMessage(chat_id, 'preparing status...')
                                bot.sendMessage(62922848,
                                                "copter ip: %s" % get_ip() + '\n' + dronekit.get_status() + '\nSTATE: %s' % STATE)
                            elif msg['text'] == '/stop':
                                # остановка всех операций в MACHINE STATE и перевод в IDLE
                                bot.sendMessage(chat_id, 'stop all operations, go to IDLE STATE')
                            elif msg['text'] == '/help':
                                bot.sendMessage(chat_id,
                                                'This Bot created for control copter\nА вообще во мне семь всевдопараллельных потоков и меня это устраивает')
                            else:
                                bot.sendMessage(chat_id, 'Ошибка 4! Некорректная текстовая команда')
                        elif content_type == 'location':
                            # расчет возможности полета в заданные координаты и построение полетного задания
                            # bot.sendMessage(chat_id, 'preparing mission...')
                            bot.sendMessage(chat_id,
                                            str(msg['location']['latitude']) + '\n' + str(msg['location']['longitude']))
                        else:
                            bot.sendMessage(chat_id, 'Ошибка 2! Неверный тип: только text и location')
                    else:
                        bot.sendMessage(chat_id, 'Ошибка 1! Команда \"' + msg[
                            'text'] + '\" не может быть выполнена. STATE == INIT')
                else:
                    bot.sendMessage(chat_id, 'Ошибка 3! Access error!')
            bot.message_loop(handle)

            import time
            time.sleep(1.5)  # время на ответ сообщений пришедших в выключенный период

            if DEBUG:
                print ('Connecting to APM ...')
                bot.sendMessage(62922848, 'Connecting to APM ...')
            from dronekit_functions import *
            dronekit = autocopterDronekit()  # для доступности в finally (ВРОДЕ КАК НЕ НАДО)
            if dronekit.status_of_connect:
                # global STATE
                STATE = 'IDLE'
                if DEBUG:
                    print ('Connect successful!')
                    bot.sendMessage(62922848, 'Connect successful!')
                    print ('Listening ...')
                    bot.sendMessage(62922848, 'Listening ...')
                    # Keep the program running.
            pass
        elif STATE == 'IDLE':
            pass
        elif STATE == 'TAKEOFF':
            pass
        elif STATE == 'LOITER':
            pass
        elif STATE == 'RTL':
            pass
        elif STATE == 'AUTO':
            pass
        elif STATE == 'LAND':
            pass
        elif STATE == 'GUIDED':
            pass
        else:
            pass
        import time
        time.sleep(1)
finally:
    dronekit.disconnect
    print('\n######################################################')
    print('\nFinally success!\n')
    print('######################################################\n')
