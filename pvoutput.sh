#!/bin/bash
# ---------------------------------------------------------------
# A script to keep the CombinePVOutputSystems.py script running.
# Add to your crontab to run once a day, e.g. at 05:04 and at reboot
# 4 5 * * * ~/solis/pvoutput.sh > /dev/null
# @reboot sleep 243 && ~/solis/pvoutput.sh > /dev/null
# ---------------------------------------------------------------
script_name=$(basename -- "$0")
cd ~/solis

now=$(date)
if pidof -x "$script_name" -o $$ >/dev/null;then
   echo "$now: $script_name already running" >> pvoutput.crontab.log 2>&1
   exit 1
fi
echo "ERROR: $now: $script_name NOT running" >> pvoutput.crontab.log 2>&1
/usr/bin/python -u ~/solis/CombinePVOutputSystems.py >> pvoutput.log 2>&1 
