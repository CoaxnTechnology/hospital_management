#!/bin/bash
cd /home/vagrant
source venv/bin/activate
pip install django-tinymce
cd echo
python manage.py migrate
python manage.py create_types_ordonnances
python manage.py collectstatic