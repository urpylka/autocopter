#! /usr/bin/env python

#
# Copyright 2017-2018 Artem B. Smirnov
# Licensed under the Apache License, Version 2.0
#

# -*- coding: utf8 -*-

class CheckInternet(object):
    """
    Класс для мониторинга интернета

    Может сделать класс Internet c методами connect, dissconnet, reconnect
    """

    def __init__(self):
        self.check_interval = 1
        self.check_host = 'ya.ru'
        self.get_ip_service_address = "ipv4.icanhazip.com"
        self.get_ip_service_proto = "GET"
        self.get_ip_service_request = "/"

        self.connection_established = threading.Event()
        self.__thread = Thread(target=self.__loop)
        self.__thread.daemon = True
        self.__thread.start()

    def __loop(self):
        while True:
            if self.check(self.check_host): self.connection_established.set()
            else self.connection_established.clear()
            time.sleep(self.check_interval)

    def check(host):
        try:
            socket.gethostbyaddr(host)
        except socket.gaierror:
            return False
        return True

    def get_ip():
        if connection_established.is_set():
            conn = http.client.HTTPConnection(self.get_ip_service_address)
            try:
                conn.request(self.get_ip_service_proto, self.get_ip_service_request)
                http_responce = conn.getresponse().read()
                IP_REGEX = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
                if re.match(IP_REGEX, http_responce): return http_responce
                else: raise ValueError("Не удалось вычислить IP адрес.\nОтвет от '%s' некорректен.", self.get_ip_service_address)
            except Exception as e: raise SystemError("Не удалось вычислить IP адрес.\nВозникла ошибка: %s", e.strerror)
        else raise ConnectionError("Не удалось вычислить IP адрес.\nНет соединения с интернетом, проверен доступ до '%s'", self.test_host)
