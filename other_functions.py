#!/usr/bin/python
# -*- coding: utf8 -*-

import http.client
import socket, time

def check_internet():
    try:
        socket.gethostbyaddr('ya.ru')
    except socket.gaierror:
        return False
    return True

def wait_internet():
    while not check_internet():
        time.sleep(1)

def get_ip():
    conn = http.client.HTTPConnection("smirart.ru")
    conn.request("GET", "/ip")
    return conn.getresponse().read()
