cp /home/pi/autocopter/autocopter /etc/init.d/autocopter


sudo chmod +x /etc/init.d/autocopter
sudo chown root:root /etc/init.d/autocopter
sudo update-rc.d autocopter defaults

https://confluence.atlassian.com/kb/starting-service-on-linux-throws-a-no-such-file-or-directory-error-794203722.html

написание своего питон приложения как сервиса
http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/