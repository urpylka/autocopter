#!/usr/bin/env python
# -*- coding: utf8 -*-
#import time
#time.sleep(180000)
import socket, time
def check_internet():
    try:
        socket.gethostbyaddr('ya.ru')
    except socket.gaierror:
        return False
    return True
while not check_internet():
    time.sleep(1)
def get_ip():
    import http.client
    conn = http.client.HTTPConnection("smirart.ru")
    conn.request("GET", "/ip")
    return conn.getresponse().read()
vehicle = None #для доступности в finally
try:
    # START TELEGRAM BOT
    import sys, telepot
    def handle(msg):
        """хендлер выполняется в отдельном потоке, вызывается событием на подобие блокирующей очереди"""
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)
        if chat_id == 62922848:
            if content_type == 'text':
                if msg['text'] == '/start':
                    # попытка совершения полета в указанную точку в режиме APM AUTO
                    bot.sendMessage(chat_id, 'try starting mission...')
                elif msg['text'] == '/status':
                    # вывод информации о коптере, ip, заряд батареи
                    #bot.sendMessage(chat_id, 'preparing status...')
                    bot.sendMessage(62922848, "copter ip: %s" % get_ip() + '\n' + get_status(vehicle) + '\nSTATE: %s' % STATE)
                elif msg['text'] == '/stop':
                    # остановка всех операций в MACHINE STATE и перевод в IDLE
                    bot.sendMessage(chat_id, 'stop all operations, go to IDLE STATE')
                elif msg['text'] == '/help':
                    bot.sendMessage(chat_id,
                                    'This Bot created for control copter\nА вообще во мне семь всевдопараллельных потоков и меня это устраивает')
                else:
                    bot.sendMessage(chat_id, 'Bad command!')
            elif content_type == 'location':
                # расчет возможности полета в заданные координаты и построение полетного задания
                #bot.sendMessage(chat_id, 'preparing mission...')
                bot.sendMessage(chat_id, str(msg['location']['latitude'])+'\n'+str(msg['location']['longitude']))
            else:
                bot.sendMessage(chat_id, 'Bad command!')
        else:
            bot.sendMessage(chat_id, 'Access error!')
    TOKEN = sys.argv[1]  # get token from command-line
    bot = telepot.Bot(TOKEN)
    bot.message_loop(handle)
    print ('Listening ...')
    ###########################################
    # Connect to the Vehicle (in this case a UDP endpoint)

    # здесь же запуск вспомогательных потоков
    ###########################################
    bot.sendMessage(62922848, "Starting main daemon, copter is online: %s" % get_ip())
    import time
    # Keep the program running.
    STATE = 'IDLE'
    while 1:
        if STATE == 'IDLE':
            pass
        elif STATE == 'FLY':
            pass
        elif STATE == 'EMERGY_STOP':
            pass
        else:
            pass
        time.sleep(1)
finally:

    print('\n######################################################')
    print('\nFinally success!\n')
    print('######################################################\n')
