#!/usr/bin/env python
# -*- coding: utf8 -*-
from log_and_messages import *
import sys, telepot, time, traceback, os.path
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
                #TOKEN = sys.argv[1]  # get token from command-line
                token_path = "/home/pi/autocopter/telegrambot.token"
                if os.path.isfile(token_path):
                    f = open(token_path, 'r')
                    TOKEN = f.readline().rstrip('\n')
                    f.close()
                else:
                    print "Файл " + token_path + " не найден! Dronekit не будет доступен в finnaly, не правильно отработает lam."
                    break
                bot = telepot.Bot(TOKEN)
                # ==========================================================================================================
                lam = log_and_messages(bot, MY_CHAT_ID, DEBUG)
                lam.deb_pr_tel("Autocopter is online: %s" % get_ip())

                def handle(msg):
                    """хендлер выполняется в отдельном потоке, вызывается событием на подобие блокирующей очереди"""
                    content_type, chat_type, chat_id = telepot.glance(msg)
                    if DEBUG:
                        print(content_type, chat_type, chat_id)
                    if chat_id == MY_CHAT_ID:
                        if content_type == 'text':
                            lam.deb_pr_tel(dronekit.new_command(STATE, msg['text']))
                        elif content_type == 'location':
                            lam.deb_pr_tel(dronekit.new_command(STATE, 'create_mission', msg['location']))
                        elif content_type == 'sticker':
                            dronekit.get_location(bot,MY_CHAT_ID)
                        else:
                            lam.deb_pr_tel('Ошибка 2! Неверный тип: только text и location')
                    else:
                        lam.deb_pr_tel('Ошибка 1! Access error!')
                bot.message_loop(handle)
                time.sleep(1.5)  # время на ответ сообщений пришедших в выключенный период

                lam.deb_pr_tel('Connecting to APM ...')
                dronekit = autocopterDronekit(lam.deb_pr_tel)  # для доступности в finally (ВРОДЕ КАК НЕ НАДО)
                if dronekit.status_of_connect:
                    nextState = 'IDLE'
                    lam.deb_pr_tel('Connect successful!\nListening ...')
                    # Keep the program running.
            except Exception as ex:
                lam.deb_pr_tel('Произошла ошибка:\n' + ex.message + "\n" + traceback.format_exc() + '\nТаймаут 10 сек. Переход из состояниия ' + STATE + ', переход в состояние ' + nextState)
                time.sleep(10)
            finally:
                STATE = nextState
        elif STATE == 'IDLE':
            nextState = 'IDLE'
            try:
                nextState = dronekit.IDLE(lam)
            except Exception as ex:
                lam.deb_pr_tel('Произошла ошибка:\n' + ex.message + "\n" + traceback.format_exc() + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        elif STATE == 'TAKEOFF':
            nextState = 'TAKEOFF'
            try:
                nextState = dronekit.TAKEOFF(lam)
            except BaseException:
                lam.deb_pr_tel(
                    'Произошла ошибка:\n' + BaseException.message + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        elif STATE == 'HOVER':
            nextState = 'HOVER'
            try:
                nextState = dronekit.HOVER(lam)
            except Exception as ex:
                lam.deb_pr_tel(
                    'Произошла ошибка:\n' + ex.message + "\n" + traceback.format_exc() + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        elif STATE == 'RTL':
            nextState = 'RTL'
            try:
                nextState = dronekit.RTL(lam)
            except Exception as ex:
                lam.deb_pr_tel(
                    'Произошла ошибка:\n' + ex.message + "\n" + traceback.format_exc() + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        elif STATE == 'AUTO':
            nextState = 'AUTO'
            try:
                nextState = dronekit.AUTO(lam)
            except Exception as ex:
                lam.deb_pr_tel(
                    'Произошла ошибка:\n' + ex.message + "\n" + traceback.format_exc() + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        elif STATE == 'LAND':
            nextState = 'LAND'
            try:
                nextState = dronekit.LAND(lam)
            except Exception as ex:
                lam.deb_pr_tel(
                    'Произошла ошибка:\n' + ex.message + "\n" + traceback.format_exc() + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        elif STATE == 'GOTO':
            nextState = 'GOTO'
            try:
                nextState = dronekit.GOTO(lam)
            except Exception as ex:
                lam.deb_pr_tel(
                    'Произошла ошибка:\n' + ex.message + "\n" + traceback.format_exc() + '\nв состоянии ' + STATE + ', переход в состояние ' + nextState)
            finally:
                STATE = nextState
        else:
            nextState = 'IDLE'
            lam.deb_pr_tel('Произошла ошибка: не существует состояния ' + STATE + ', переход в состояние ' + nextState)
            STATE = nextState
        time.sleep(3) # для обеспечения задержки в 3 сек в случае возникновения повторяющейся ошибки
finally:
    dronekit.disconnect
    print('\n######################################################')
    print('\nFinally success!\n')
    print('######################################################\n')