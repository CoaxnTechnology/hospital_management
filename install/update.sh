#!/usr/bin/env bash

cd /home/vagrant

DIR="/media/sf_partage/"
if [ -d "$DIR" ]; then
	echo "Virtual box image"
	sudo cp /media/sf_partage/build.zip -d .
	sudo chown vagrant build.zip
fi

unzip -o build.zip -d /home/vagrant/echo
cd echo
chmod +x version_update.sh
./version_update.sh