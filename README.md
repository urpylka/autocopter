# Autocopter

Autocopter allow control your APM compatible copter with Telegram messenger.

This software must be running on companion computer connected to APM using Serial (USB), TCP or UDP. Recommended embedded platform is Raspberry Pi.

For configure internet on your drone (Raspberry Pi) use [modem_keeper](https://github.com/urpylka/modem_keeper).

![](telegram.jpg)

## Install

Execute script:
```bash
git clone https://github.com/urpylka/autocopter.git

pip install -r autocopter/requirements.txt

# Create config
cat <<EOF | sudo tee $(pwd)/autocopter/autocopter.json > /dev/null
{
    "telegram":
    {
        "token":"YOUR_TOKEN",
        "proxy":"YOUR_TELEGRAM_HTTP_PROXY_OR_null",
        "chat_id":"YOUR_CHAT_ID",
        "debug":"True"
    },
    "autocopter":
    {
        "connection_string":"tcp:127.0.0.1:14600"
    }
}
EOF

# Create service
cat <<EOF | sudo tee /lib/systemd/system/autocopter.service > /dev/null
[Unit]
Description=Autocopter

[Service]
ExecStart=$(pwd)/autocopter/autocopter.py $(pwd)/autocopter/autocopter.json
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

python autocopter/autocopter.py "CONNECTION_STR" "BOT_TOKEN" "CHAT_ID" "PROXY" "DEBUG"

# or
python autocopter/autocopter.py "PATH_TO_CONFIG"
```

## MAVGateway - service for run MAVProxy

An option you can install MAVProxy for connecting your APM with many agents (f.e. laptop, dronekit).

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
* сделать нормальное описание: помимо README выложить видео и скрины
* Добавить структуру и диаграмму состояний
* надо написать параллельную реализацию для выполенения фукнций dronekit (старая идея)
* Подумать как связать с ros (через класс общий для dronekit и mavros)???
* Вынести статес?
