# Autocopter

Autocopter allow control your APM compatible copter with Telegram messenger.

## TODO
* вынести софт для поддержания соединения с модемом sakis3g+umtskeeper (папка 3g_modem) и rssh
* сделать нормальное описание: помимо README выложить видео и скрины
* сделать нормальный конфиг файл (избавиться от chat_id, передачи токена через sys.argv[1])
* добавить диаграмму структуры
* описать requirements
* надо написать параллельную реализацию для выполенения фукнций dronekit (старая идея)

External libraries:
dronekit-python, telepot

## Install
Download from bulid/latest.sh file to your home direstory.
```bash
git clone https://github.com/urpylka/autocopter.git
/home/pi/latest.sh
```
## Launch
```bash
python autocopter/autocopter.py 'YOUR_BOT_TOKEN'
```

