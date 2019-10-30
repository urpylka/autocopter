#! /usr/bin/env python

#
# Copyright 2017-2018 Artem B. Smirnov
# Licensed under the Apache License, Version 2.0
#

# -*- coding: utf8 -*-

# https://dev.to/karn/building-a-simple-state-machine-in-python

class Autocopter(object):
    """
    Main class
    TODO: write about it
    """

    def __init__(self):
        """
        Initialize the components
        """

        # Нужна система event'ов

        # Может все включается здесь
        # А все проверки уже в InitState
        self.check_internet = CheckInternet()
        self.fcu = ClassFcuConnect()
        self.telegram = TelegramBot()

        # Start with a default state.
        self.state = InitState()

    def on_event(self, event):
        """
        This is the bread and butter of the state machine. Incoming events are
        delegated to the given states which then handle the event. The result is
        then assigned as the new state.
        """
        # The next state will be the result of the on_event function.
        self.state = self.state.on_event(event)

    def new_command(self, command):
        """
        This is the bread and butter of the state machine. Incoming events are
        delegated to the given states which then handle the event. The result is
        then assigned as the new state.
        """
        # The next state will be the result of the on_event function.
        self.state = self.state.new_command(command)
