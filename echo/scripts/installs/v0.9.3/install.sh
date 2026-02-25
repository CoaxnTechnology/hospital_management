#!/bin/bash
cd /home/vagrant
source venv/bin/activate
pip install graypy
cd echo
python manage.py loaddata liste_choix