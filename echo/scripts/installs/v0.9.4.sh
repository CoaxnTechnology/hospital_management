#!/bin/bash
cd /home/vagrant
source venv/bin/activate
cd echo
python manage.py loaddata motifs_consultation