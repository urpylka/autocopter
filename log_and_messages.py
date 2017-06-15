#!/usr/bin/python
# -*- coding: utf8 -*-
class log_and_messages(object):
    def __init__(self,bot,DEBUG=True,chatId=62922848):
        self._bot = bot
        self._DEBUG = DEBUG
        self._chatId = chatId
        self._bot.sendMessage(self._chatId, 'msg2')
    def deb_pr_tel(self,msg):
        if self._DEBUG:
            print(msg)
            self._bot.sendMessage(self._chatId, msg)