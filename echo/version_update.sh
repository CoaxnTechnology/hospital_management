#!/bin/bash
PASS="Expert@2021"
cd
source ./venv/bin/activate
cd ./echo
pip install opencv-python
pip install pymemcache
echo $PASS|sudo -S apt install memcached dos2unix
echo $PASS|sudo usermod -a -G vagrant www-data
python manage.py migrate
python manage.py loaddata motifs_consultation
python manage.py loaddata liste_choix
python manage.py loaddata sous_categories_antecedents
python manage.py loaddata dossiers_patient
python manage.py loaddata motifs_rdv
python manage.py create_groups
python manage.py change_types_ordonnances
chmod +x dicom.sh & dos2unix dicom.sh
chmod +x fix_chat.sh & dos2unix fix_chat.sh
chmod +x install_dicom.sh & dos2unix install_dicom.sh
chmod +x backup.sh & dos2unix backup.sh
chmod +x send_slack_msg.sh & dos2unix send_slack_msg.sh
./install_dicom.sh
echo $PASS|sudo -S supervisorctl restart all