#!/usr/bin/env bash

ssh -N -R 5760:localhost:5760 -i /home/pi/.ssh/id_rsa urpylka@smirart.ru -p32122
#ssh -q -N -R 5760:localhost:5760 -i /home/pi/.ssh/id_rsa urpylka@smirart.ru -p32122
