#!/bin/bash
sudo add-apt-repository -y ppa:redislabs/redis
sudo apt update
sudo apt install -y redis-server
sudo systemctl stop redis-server
sudo sed -i 's/supervised no/supervised systemd/' /etc/redis/redis.conf
sudo systemctl start redis-server
cd
source ./venv/bin/activate
pip install channels==2.4.0
sudo supervisorctl restart all