#!/usr/bin/python
# -*- coding: utf8 -*-
class log_and_messages(object):
    def __init__(self,bot,DEBUG=True,chatId=62922848):
        self._bot = bot
        self._DEBUG = DEBUG
        self._chatId = chatId
        bot.sendMessage(62922848, 'msg2')
        self._bot.sendMessage(62922848, 'msg3')
    def deb_pr_tel(self,msg):
        if self._DEBUG:
            print(msg)
            self._bot.sendMessage(self._chatId, msg)