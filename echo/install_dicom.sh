#!/bin/bash
if [ -v DICOM_INSTALL ];
then echo "DICOM already installed";
else
echo "DICOM not installed";
cd /home/vagrant
source ./venv/bin/activate
pip install pynetdicom==1.5.3 numpy==1.19.0 pypng dataclasses
cd /home/vagrant/echo
sudo cp ./config/dicom-worklist.conf /etc/supervisor/conf.d/echo-worklist.conf
sudo cp ./config/dicom-store.conf /etc/supervisor/conf.d/echo-store.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status
export DICOM_INSTALL=1
echo "export DICOM_INSTALL=1" >> ~/.bashrc
source ~/.bashrc
fi