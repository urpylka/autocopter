#!/usr/bin/env bash

# окружение https://losst.ru/napisanie-skriptov-na-bash

cd /home/pi
rm -rf autocopter # надо сначала проверить есть интернет или нет (точнее доступ к гитхаб)
git clone https://github.com/urpylka/autocopter.git

cp -f autocopter/daemons/rssh /etc/init.d/rssh # лучше делать символьные ссылки рекурсивно
update-rc.d rssh defaults

cp -f autocopter/daemons/umtskeeper /etc/init.d/umtskeeper
update-rc.d umtskeeper defaults

cp -f autocopter/daemons/mavgateway /etc/init.d/mavgateway
update-rc.d mavgateway defaults

cp -f autocopter/daemons/autocopter /etc/init.d/autocopter
update-rc.d autocopter defaults

cp -f /home/pi/telegrambot.token /home/pi/autocopter/telegrambot.token

sudo service mavgateway restart
sudo service umtskeeper restart
sudo service rssh restart
sudo service autocopter restart
