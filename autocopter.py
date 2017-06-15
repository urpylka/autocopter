#!/usr/bin/env python
# -*- coding: utf8 -*-

from log_and_messages import *
import sys, telepot, time
from other_functions import get_ip
from dronekit_functions import *
# Устранение проблем с кодировкой UTF-8
# http://webhamster.ru/mytetrashare/index/mtb0/13566385393amcr1oegx
reload(sys)
sys.setdefaultencoding('utf8')

#dronekit = autocopterDronekit()  # для доступности в finally (ВРОДЕ КАК НЕ НАДО)


#def changeNextState(_nextState):
#    global nextState
#    nextState = _nextState
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
            TOKEN = sys.argv[1]  # get token from command-line
            bot = telepot.Bot(TOKEN)
            # ==========================================================================================================
            log_and_messages = log_and_messages(bot)
            log_and_messages.deb_pr_tel("Autocopter is online: %s" % get_ip())

            def handle(msg):
                """хендлер выполняется в отдельном потоке, вызывается событием на подобие блокирующей очереди"""
                content_type, chat_type, chat_id = telepot.glance(msg)
                print(content_type, chat_type, chat_id)
                if chat_id == 62922848:
                    # global STATE #https://foxford.ru/wiki/informatika/oblasti-vidimosti-peremennyh-v-python#!
                    if STATE != 'INIT':
                        if content_type == 'text':
                            if msg['text'] == '/start':
                                if STATE == 'IDLE':
                                    global nextIdleState
                                    nextIdleState = "TAKEOFF"
                                # попытка совершения полета в указанную точку в режиме APM AUTO
                                log_and_messages.deb_pr_tel('try starting mission...')
                            elif msg['text'] == '/status':
                                # вывод информации о коптере, ip, заряд батареи
                                # bot.sendMessage(chat_id, 'preparing status...')
                                log_and_messages.deb_pr_tel("copter ip: %s" % get_ip() + '\n' + dronekit.get_status() + '\nSTATE: %s' % STATE)
                            elif msg['text'] == '/stop':
                                dronekit.stop_takeoff = True
                                #dronekit.motors_off()
                                # остановка всех операций в MACHINE STATE и перевод в IDLE
                                log_and_messages.deb_pr_tel('stop all operations, go to IDLE STATE')
                            elif msg['text'] == '/help':
                                log_and_messages.deb_pr_tel('This Bot created for control copter\nА вообще во мне семь всевдопараллельных потоков и меня это устраивает')
                            else:
                                log_and_messages.deb_pr_tel('Ошибка 4! Некорректная текстовая команда')
                        elif content_type == 'location':
                            # расчет возможности полета в заданные координаты и построение полетного задания
                            # bot.sendMessage(chat_id, 'preparing mission...')
                            log_and_messages.deb_pr_tel(str(msg['location']['latitude']) + '\n' + str(msg['location']['longitude']))
                        else:
                            log_and_messages.deb_pr_tel('Ошибка 2! Неверный тип: только text и location')
                    else:
                        log_and_messages.deb_pr_tel('Ошибка 1! Команда \"' + msg['text'] + '\" не может быть выполнена. STATE == INIT')
                else:
                    log_and_messages.deb_pr_tel('Ошибка 3! Access error!')
            bot.message_loop(handle)

            time.sleep(1.5)  # время на ответ сообщений пришедших в выключенный период

            log_and_messages.deb_pr_tel('Connecting to APM ...')
            dronekit = autocopterDronekit()  # для доступности в finally (ВРОДЕ КАК НЕ НАДО)
            if dronekit.status_of_connect:
                # global STATE
                STATE = 'IDLE'
                log_and_messages.deb_pr_tel('Connect successful!\nListening ...')
                    # Keep the program running.
        elif STATE == 'IDLE':
            nextIdleState = 'IDLE'  # 'TAKEOFF'
            dronekit.switch_to_IDLE(log_and_messages)
            # здесь крутимся за счет следующего цикла
            while STATE == 'IDLE':
                if nextIdleState != 'IDLE':
                    if nextIdleState == 'TAKEOFF':
                        STATE = 'TAKEOFF'
                        log_and_messages.deb_pr_tel('Switch to TAKEOFF')
                    else:
                        nextIdleState = "IDLE"
                        log_and_messages.deb_pr_tel('Из состояния IDLE можно перейти только в состояние TAKEOFF')
                time.sleep(1)
        elif STATE == 'TAKEOFF':
            nextTakeOffState = "GUIDED"
            targetAltitude = 20
            nextTakeOffState = dronekit.arm_and_takeoff(targetAltitude,log_and_messages)

            if nextTakeOffState == 'GUIDED':
                STATE = 'GUIDED'
                log_and_messages.deb_pr_tel('Switch to GUIDED')
            elif nextTakeOffState == 'AUTO':
                STATE = 'AUTO'
                log_and_messages.deb_pr_tel('Switch to AUTO')
            elif nextTakeOffState == 'GOTO':
                STATE = 'GOTO'
                log_and_messages.deb_pr_tel('Switch to GOTO')
            else:
                nextTakeOffState = "GUIDED"
                log_and_messages.deb_pr_tel('Введенное состояние некорректное: Автоматический переход из TAKEOFF в состояние GUIDED (вообще возможны AUTO и GOTO')
                time.sleep(1)
        elif STATE == 'GUIDED':
            nextGuidedState = 'GUIDED'
            dronekit.switch_to_GUIDED(log_and_messages)
            # здесь крутимся за счет следующего цикла
            while STATE == 'GUIDED':
                if nextGuidedState != 'GUIDED':
                    if nextGuidedState == 'LAND':
                        STATE = 'LAND'
                        log_and_messages.deb_pr_tel('Switch to LAND')
                    elif nextGuidedState == 'RTL':
                        STATE = 'RTL'
                        log_and_messages.deb_pr_tel('Switch to RTL')
                    elif nextGuidedState == 'AUTO':
                        STATE = 'AUTO'
                        log_and_messages.deb_pr_tel('Switch to AUTO')
                    elif nextGuidedState == 'GOTO':
                        STATE = 'GOTO'
                        log_and_messages.deb_pr_tel('Switch to GOTO')
                    else:
                        nextGuidedState = "GUIDED"
                        log_and_messages.deb_pr_tel('Из состояния GUIDED можно перейти только в состояния LAND, RTL, AUTO, GOTO')
                time.sleep(1)
        elif STATE == 'RTL':
            nextRTLState = 'RTL'
            dronekit.switch_to_RTL(log_and_messages)

            # как работает функция mode RTL сколько времени??????????

            # здесь крутимся за счет следующего цикла
            # ручной переход в LAND и IDLE напрямую невозможен
            while STATE == 'RTL':
                if nextRTLState != 'RTL':
                    if nextRTLState == 'GUIDED':
                        STATE = 'GUIDED'
                        log_and_messages.deb_pr_tel('Switch to GUIDED')
                    else:
                        nextRTLState = "RTL"
                        log_and_messages.deb_pr_tel('Из состояния RTL можно перейти только в состояния GUIDED')
                elif dronekit.onLand():
                    STATE = 'IDLE'
                    log_and_messages.deb_pr_tel('Закончен режим RTL перевод в IDLE')
                time.sleep(1)
        elif STATE == 'AUTO':
            pass
        elif STATE == 'LAND':
            pass
        elif STATE == 'GOTO':
            pass
        else:
            pass
        time.sleep(1)
finally:
    dronekit.disconnect
    print('\n######################################################')
    print('\nFinally success!\n')
    print('######################################################\n')
