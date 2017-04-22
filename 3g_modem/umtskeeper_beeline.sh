#! /bin/sh
echo "starting umtskeeper"
#скрипт который запускает демон
#по-хорошему нужно перенести данный скрипт в тело демона
#прописаны параметры подключения к сети билайн и и мегафон модему E352 (кажется), перепрошитому утилитой Huawei
#специально отключил --silent тк в init.d есть параметр --background и перенаправление потока ввода-выводы > /dev/null
/home/pi/autocopter/3g_modem/umtskeeper --sakisoperators "USBINTERFACE='0' OTHER='USBMODEM' USBMODEM='12d1:1506' APN='CUSTOM_APN' CUSTOM_APN='internet.beeline.ru' SIM_PIN='0000' APN_USER='beeline' APN_PASS='beeline'" --sakisswitches "--sudo --console" --devicename 'Huawei' --log --nat 'no'

