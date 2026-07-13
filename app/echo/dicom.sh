#!/bin/bash
cd /home/vagrant
source ./venv/bin/activate
cd ./echo
python worklist.py &
python store.py
