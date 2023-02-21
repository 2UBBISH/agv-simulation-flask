#!/usr/bin/env bash

############################
# must give rights to /var/www
############################
#mkdir "/var/www"
#chmod 777 /var/www

############################
#openresty和uwsgi相关
############################
#环境启动程序
openresty -t;
service openresty start;

############################
#uwsgi配置文件
############################
cd /www/site/com.qin/agv_simulation_flask


#必须确保pip3的版本>= 19.3,不然会安装失败
#https://pypi.org/project/opencv-python/
python3 -m pip --version
python3 -m pip install -r requirements.txt

if [[ ! -L /etc/uwsgi-emperor/vassals/agv_simulation_flask.ini ]] && [[ ! -f /etc/uwsgi-emperor/vassals/agv_simulation_flask.ini ]];then
    ln -s /www/site/com.qin/agv_simulation_flask/uwsgi/vpc_lab/agv_simulation_flask.ini  /etc/uwsgi-emperor/vassals/agv_simulation_flask.ini
fi;

############################
#重新启动uwsgi
############################
service uwsgi-emperor stop
service uwsgi-emperor start
sleep 2
service uwsgi-emperor status

echo "Success"