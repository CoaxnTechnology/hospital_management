#!/bin/bash

PASS="Expert@2021"

echo $PASS|sudo -S supervisorctl stop all

echo $PASS|sudo -S mkdir -p /media/backup/$(date +'%Y-%m-%d')

cd
mkdir -p tmp

echo $EE_VERSION >> ./tmp/version.txt
mkdir -p ./tmp/$(date +'%Y-%m-%d')
zip -r ./tmp/$(date +'%Y-%m-%d')/data.zip ./data
echo $PASS|sudo -S -u postgres pg_dump echoapp > ./tmp/$(date +'%Y-%m-%d')/db.sql

echo $PASS|sudo -S cp -R ./tmp/$(date +'%Y-%m-%d')/ /media/backup/

echo $PASS|sudo -S supervisorctl start all

status=$?
if [ $status -eq 0 ]; then
    echo "Backup succes pour $EE_COMPTE - version $EE_VERSION"
else ./echo/send_slack_msg.sh "Erreur de backup pour $EE_COMPTE - version $EE_VERSION"
fi