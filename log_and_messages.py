#!/usr/bin/python
# -*- coding: utf8 -*-
class log_and_messages(object):
    def __init__(self,bot,chatId,DEBUG=True):
        self._bot = bot
        self._DEBUG = DEBUG
        self._chatId = chatId
    def deb_pr_tel(self,msg):
        if self._DEBUG:
            print(msg)
            self._bot.sendMessage(self._chatId, msg)