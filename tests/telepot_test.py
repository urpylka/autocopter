#!/usr/bin/python
# -*- coding: utf8 -*-

# USE: python ./tepelot_test.py 'BOT_TOKEN' ['CHAT_ID']

import sys, telepot
import http.client

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        bot.sendMessage(chat_id, msg['text'])
        msg['text'] == '/start':
    else:
        bot.sendMessage(chat_id, 'Bad command!')

bot = telepot.Bot(sys.argv[1])
bot.message_loop(handle)
print ('Listening ...')

if (len(sys.argv) == 3):
    bot.sendMessage(sys.argv[2], "Hello world!")
