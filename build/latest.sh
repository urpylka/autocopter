#! /bin/sh
cd /home/pi
rm -rf autocopter
git clone https://github.com/urpylka/autocopter.git

chmod +x autocopter/build/*
chmod +x autocopter/autocopter.py

cp -f autocopter/daemons/umtskeeper /etc/init.d/umtskeeper
chmod +x /etc/init.d/umtskeeper
chown root:root /etc/init.d/umtskeeper
update-rc.d umtskeeper defaults

cp -f autocopter/daemons/mavgateway /etc/init.d/mavgateway
chmod +x /etc/init.d/mavgateway
chown root:root /etc/init.d/mavgateway
update-rc.d mavgateway defaults

cp -f autocopter/daemons/autocopter /etc/init.d/autocopter
chmod +x /etc/init.d/autocopter
chown root:root /etc/init.d/autocopter
update-rc.d autocopter defaults


# FOR DEBUG
#python autocopter/autocopter.py 'TOKEN'
