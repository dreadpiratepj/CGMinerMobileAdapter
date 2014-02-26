#!/bin/bash
SETTINGS_FILE="settings.conf"
PYTHON_FILE="CGMinerMobileAdapter.py"
INSTALLATION_FOLDER="/opt/CGMinerMobileAdapter/"
INSTALLATION_PATH=$INSTALLATION_FOLDER$PYTHON_FILE
SCREEN_COMMAND="screen -dmS MobileMiner python "$INSTALLATION_PATH
RC_LOCAL_PATH="/etc/rc.local"


mkdir -p $INSTALLATION_FOLDER
cp $PYTHON_FILE $INSTALLATION_PATH

echo -n "Enter e-mail: "
read email

echo -n "Enter machine name: "
read machineName

echo -n "Enter application key: "
read appKey

touch settings.conf
echo $email > $INSTALLATION_FOLDER$SETTINGS_FILE
echo $appKey >> $INSTALLATION_FOLDER$SETTINGS_FILE
echo $machineName >> $INSTALLATION_FOLDER$SETTINGS_FILE

screen -X -S MobileMiner quit
$SCREEN_COMMAND

if ! grep -q "$SCREEN_COMMAND" "/etc/rc.local"; then
        echo $SCREEN_COMMAND >> $RC_LOCAL_PATH
fi

apt-get install python-pip -y
pip install argparse


