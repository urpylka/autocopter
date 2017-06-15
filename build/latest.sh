#!/usr/bin/env bash
# окружение https://losst.ru/napisanie-skriptov-na-bash
#service autocopter stop
#service mavgateway stop
#service umtskeeper stop
#service rssh stop

cd /home/pi
rm -rf autocopter # надо сначала проверить есть интернет или нет (точнее доступ к гитхаб)
git clone https://github.com/urpylka/autocopter.git

chmod +x autocopter/build/*

chmod +x autocopter/rssh.py
cp -f autocopter/daemons/rssh /etc/init.d/rssh # лучше делать символьные ссылки рекурсивно
chmod +x /etc/init.d/rssh
chown root:root /etc/init.d/rssh
update-rc.d rssh defaults

cp -f autocopter/daemons/umtskeeper /etc/init.d/umtskeeper
chmod +x /etc/init.d/umtskeeper
chown root:root /etc/init.d/umtskeeper
update-rc.d umtskeeper defaults

chmod +x autocopter/3g_modem/umtskeeper_beeline.sh
chmod +x autocopter/3g_modem/umtskeeper
chmod +x autocopter/3g_modem/sakis3g
cp -f autocopter/daemons/mavgateway /etc/init.d/mavgateway
chmod +x /etc/init.d/mavgateway
chown root:root /etc/init.d/mavgateway
update-rc.d mavgateway defaults

chmod +x autocopter/autocopter.py
cp -f autocopter/daemons/autocopter /etc/init.d/autocopter
chmod +x /etc/init.d/autocopter
chown root:root /etc/init.d/autocopter
update-rc.d autocopter defaults

sudo service mavgateway restart
sudo service umtskeeper restart
sudo service rssh restart
sudo service autocopter restart

# FOR DEBUG
#python autocopter/autocopter.py 'TOKEN'
