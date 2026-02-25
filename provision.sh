#!/usr/bin/env bash

cd
unzip -o build.zip -d echo
mkdir data

unzip -o install.zip -d install
cp ./install/update.sh update.sh
chmod +x update.sh

sudo apt -y update
sudo apt -y install nginx
sudo service nginx start

# set up nginx configuration
cd
sudo cp ./install/provision/site.conf /etc/nginx/sites-available/default
sudo service nginx restart

#PgSql
sudo apt -y install postgresql postgresql-contrib libpq-dev python3.8-dev
sudo -u postgres psql postgres  -c "CREATE USER django WITH PASSWORD 'Owbq4rT4_RqC'"
sudo -u postgres psql postgres  -c "ALTER ROLE django SET client_encoding TO 'utf8'"
sudo -u postgres psql postgres  -c "ALTER ROLE django SET default_transaction_isolation TO 'read committed'"
sudo -u postgres psql postgres  -c "ALTER ROLE django SET timezone TO 'UTC'"
sudo -u postgres psql postgres  -c "CREATE DATABASE echoapp WITH ENCODING 'UTF8' TEMPLATE template0"
sudo -u postgres psql postgres  -c "GRANT ALL PRIVILEGES ON DATABASE echoapp TO django"

cd
sudo -u postgres psql echoapp < ./install/echoapp_db_export.sql 

 # Install python / pip
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt install -y python3.8 python3-pip virtualenv supervisor python3.8-distutils

# Create virtual env
cd
virtualenv -p /usr/bin/python3.8 venv
source venv/bin/activate

# Install gunicorn and daphne
cd echo
pip install -r requirements.txt
python manage.py migrate --fake-initial
python manage.py loaddata apps/core/fixtures/*.json

sudo cp ../install/provision/gunicorn.conf /etc/supervisor/conf.d/echo-gunicorn.conf
sudo cp ../install/provision/daphne.conf /etc/supervisor/conf.d/echo-daphne.conf

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status

sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
gsettings set org.gnome.desktop.interface enable-animations false
gsettings set org.gnome.desktop.screensaver lock-enabled false
gsettings set org.gnome.desktop.lockdown disable-lock-screen 'true'

sudo apt install -y openssh-server