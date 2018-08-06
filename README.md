# Autocopter

Autocopter allow control your APM compatible copter with Telegram messenger.

![](telegram.jpg)

## Install

1. Install requrements:
    * Install python libraries: dronekit-python, telepot
    * Install MAVProxy & start service

2. Execute script:
```bash
git clone https://github.com/urpylka/autocopter.git

cat <<EOF | sudo tee /lib/systemd/system/autocopter.service > /dev/null
[Unit]
Description=Autocopter

[Service]
ExecStart=$(pwd)/autocopter/autocopter.py 'BOT_TOKEN' 'CHAT_ID'
Restart=on-abort

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable autocopter
sudo systemctl start autocopter
```
## Manual launch
```bash
# Stop daemon if running
sudo systemctl stop autocopter

python autocopter/autocopter.py 'BOT_TOKEN' 'CHAT_ID'
```

## MAVGateway - service for run MAVProxy
```bash
cat <<EOF | sudo tee /lib/systemd/system/mavgateway.service > /dev/null
[Unit]
Description=MAVGateway

[Service]
ExecStart=/usr/local/bin/mavproxy.py --master=/dev/ttyAMA0,57600 --out=tcpin:0.0.0.0:5760 --out=tcpin:127.0.0.1:14600 --daemon
Restart=on-abort

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable mavgateway
sudo systemctl start mavgateway
```

## TODO
* вынести софт для поддержания соединения с модемом sakis3g+umtskeeper (папка 3g_modem)
* сделать нормальное описание: помимо README выложить видео и скрины
* сделать нормальный конфиг файл для токена и chat_id
* добавить диаграмму структуры
* надо написать параллельную реализацию для выполенения фукнций dronekit (старая идея)
* добавить requrements.txt
