#!/usr/bin/python
# -*- coding: utf8 -*-

# http://telepot.readthedocs.io/en/latest/

import sys
import time
import telepot
from telepot.loop import MessageLoop

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    print params

    if content_type == 'text':
        bot.sendMessage(chat_id, msg['text'])

TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)

#telepot.api.set_proxy('http://........')
#telepot.api.set_proxy('http://........', ('username', 'password'))

MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
