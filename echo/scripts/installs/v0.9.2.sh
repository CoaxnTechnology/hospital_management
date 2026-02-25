#!/bin/bash
sudo apt update
sudo apt install -y redis-server
cd /home/vagrant
source venv/bin/activate
pip install django-clearcache
pip install django-redis
pip install django-select2
cd echo
python manage.py migrate
python manage.py loaddata liste_choix
sudo supervisorctl restart all