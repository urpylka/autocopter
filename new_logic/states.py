#! /usr/bin/env python

#
# Copyright 2017-2018 Artem B. Smirnov
# Licensed under the Apache License, Version 2.0
#

# -*- coding: utf8 -*-

class BaseState(object):
    """
    Base class for state
    """
    
    def __init__(self):
        print 'Processing current state:', str(self)
        self.__thread = Thread(target=self.do_state)
        self.__thread.daemon = True
        self.__thread.start()

    def __del__(self):
        """
        TODO
        """
        print('Destructor called, vehicle deleted.')

    def do_state(self):
        """
        Handle 'do_state' that are delegated to this State.
        """
        raise NotImplementedError('Метод do_state не определен.')

    def on_event(self, event):
        """
        Handle 'on_event' that are delegated to this State.
        """
        raise NotImplementedError('Метод on_event не определен.')

    def new_command(self, command):
        """
        Handle 'new_command' that are delegated to this State.
        """
        raise NotImplementedError('Метод new_command не определен.')

    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.
        """
        return self.__str__()

    def __str__(self):
        """
        Returns the name of the State.
        """
        return self.__class__.__name__

class InitState(BaseState):
    """
    The state which prepare drone

    Mixins  https://www.ianlewis.org/en/mixins-and-python
    Locks   http://www.quizful.net/post/thread-synchronization-in-python
    """

    def do_state(self):

        # CHECK INTERNET CONNECTION
        # Может сделать не просто блокировку, а включение интернета

        CheckInternet.connection_established.wait()

        # INITIALIZATION TELEGRAM BOT

        # Может телеграм должен инициализироваться вообще не здесь, а в Autocopter,
        # а для отправки сообщений с помощью него использовать Mixin
        print "Try send message..."

        # Может для вывода сообщений сделать специальный метод в классе и в него миксином добавлять уже телеграмм итд
        self.debug_message("Autocopter is online: %s" % get_ip())
        self.debug_message("STATE = %s" % self.current_state)

        self.bot.start_handler()
        time.sleep(1.5)  # время на ответ сообщений пришедших в выключенный период

        # INITIALIZATION FCU CONNECTION
        while True:
            try:
                self.debug_message("Connecting to APM ...")
                # http://python.dronekit.io/automodule.html#dronekit.connect
                # функция долгая (пишет через функцию status_printer)
                self._vehicle = connect(self.connection_string, wait_ready = True, status_printer = self.debug_message)

                if self._status_of_connect:
                    self.debug_message("Connect successful!")
                    # next_state = States.IDLE
                    # self.debug_message("Успешное завершение состояния %s" % self.current_state + " переключение в состояние %s" % next_state)
                    # self.current_state = next_state
                    # break

                    # может и не идле стейт может надо смотреть задание и сразу переходить в нужное
                    return IdleState()

            except Exception as ex:
                #self.debug_message("Ошибка в состоянии %s" % self.current_state + ":\n" + ex.message + "\n" + traceback.format_exc() + "\n")
                self.debug_message("Connection failed!")
                self.debug_message("Timeout 10s")
                time.sleep(10)

    def on_event(self, event):
        if event == 'have_internet':
            self.
        elif event == 'unlock':
            return UnlockedState()
        # возвращение самого себя скорее всего перезагрузит все потоки либо создаст дубликаты
        return self 

