#! /bin/sh
cd /home/pi
rm -rf autocopter
git clone https://github.com/urpylka/autocopter.git
chmod +x /home/pi/autocopter/build/*
#python autocopter/autocopter.py 'TOKEN'
