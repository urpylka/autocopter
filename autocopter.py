#!/usr/bin/env python
# -*- coding: utf8 -*-

from log_and_messages import *
import sys, telepot, time, traceback
from dronekit_functions import *
# ====================================================================================
# Устранение проблем с кодировкой UTF-8
# http://webhamster.ru/mytetrashare/index/mtb0/13566385393amcr1oegx
reload(sys)
sys.setdefaultencoding('utf8')
# ====================================================================================
DEBUG = True
MY_CHAT_ID = 62922848
STATE = 'INIT'
try:
    while True:
        if STATE == 'INIT':
            nextState = 'INIT'
            try:
                # ==========================================================================================================
                # блокировка до тех пор, пока не будет соединения с интернетом
                from other_functions import wait_internet
                wait_internet()
                # ===========================================================================================================
                # START TELEGRAM BOT
                TOKEN = sys.argv[1]  # get token from command-line
                bot = telepot.Bot(TOKEN)
                # ==========================================================================================================
                log_and_messages = log_and_messages(bot, MY_CHAT_ID, DEBUG)
                log_and_messages.deb_pr_tel("Autocopter is online: %s" % get_ip())

                def handle(msg):
                    """хендлер выполняется в отдельном потоке, вызывается событием на подобие блокирующей очереди"""
                    content_type, chat_type, chat_id = telepot.glance(msg)
                    if DEBUG:
                        print(content_type, chat_type, chat_id)
                    if chat_id == MY_CHAT_ID:
                        if content_type == 'text':
                            log_and_messages.deb_pr_tel(dronekit.new_command(STATE, msg['text']))
                        elif content_type == 'location':
                            log_and_messages.deb_pr_tel(dronekit.new_command(STATE, 'create_mission', msg['location']))
                        else:
                            log_and_messages.deb_pr_tel('Ошибка 2! Неверный тип: только text и location')
                    else:
                        log_and_messages.deb_pr_tel('Ошибка 1! Access error!')
                bot.message_loop(handle)
                time.sleep(1.5)  # время на ответ сообщений пришедших в выключенный период

                log_and_messages.deb_pr_tel('Connecting to APM ...')
                dronekit = autocopterDronekit(log_and_messages.deb_pr_tel)  # для доступности в finally (ВРОДЕ КАК НЕ НАДО)
                if dronekit.status_of_connect:
                    nextState = 'IDLE'
                    log_and_messages.deb_pr_tel('Connect successful!\nListening ...')
                log_and_messages.deb_pr_tel(dronekit.status())
                    # Keep the program running.
            except BaseException as ex:
                log_and_messages.deb_pr_tel('Произошла ошибка:\n' + ex.message + "\n" + traceback.format_exc() + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        elif STATE == 'IDLE':
            nextState = 'IDLE'
            try:
                nextState = dronekit.IDLE(log_and_messages)
            except BaseException:
                log_and_messages.deb_pr_tel('Произошла ошибка:\n' + BaseException.message + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        elif STATE == 'TAKEOFF':
            nextState = 'TAKEOFF'
            try:
                nextState = dronekit.TAKEOFF(log_and_messages)
            except BaseException:
                log_and_messages.deb_pr_tel(
                    'Произошла ошибка:\n' + BaseException.message + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        elif STATE == 'GUIDED':
            nextState = 'GUIDED'
            try:
                nextState = dronekit.GUIDED(log_and_messages)
            except BaseException:
                log_and_messages.deb_pr_tel(
                    'Произошла ошибка:\n' + BaseException.message + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        elif STATE == 'RTL':
            nextState = 'RTL'
            try:
                nextState = dronekit.RTL(log_and_messages)
            except BaseException:
                log_and_messages.deb_pr_tel(
                    'Произошла ошибка:\n' + BaseException.message + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        elif STATE == 'AUTO':
            nextState = 'AUTO'
            try:
                nextState = dronekit.AUTO(log_and_messages)
            except BaseException:
                log_and_messages.deb_pr_tel(
                    'Произошла ошибка:\n' + BaseException.message + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        elif STATE == 'LAND':
            nextState = 'LAND'
            try:
                nextState = dronekit.LAND(log_and_messages)
            except BaseException:
                log_and_messages.deb_pr_tel(
                    'Произошла ошибка:\n' + BaseException.message + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        elif STATE == 'GOTO':
            nextState = 'GOTO'
            try:
                nextState = dronekit.GOTO(log_and_messages)
            except BaseException:
                log_and_messages.deb_pr_tel(
                    'Произошла ошибка:\n' + BaseException.message + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        else:
            nextState = 'IDLE'
            log_and_messages.deb_pr_tel('Произошла ошибка: не существует состояния ' + STATE + ', переход в состояние ' + nextState)
            STATE = nextState
        time.sleep(3) # для обеспечения задержки в 3 сек в случае возникновения повторяющейся ошибки
finally:
    dronekit.disconnect
    print('\n######################################################')
    print('\nFinally success!\n')
    print('######################################################\n')
