#!/bin/bash

# Prepare for installation
sudo apt-get update --allow-releaseinfo-change
sudo apt-get -y upgrade
sudo apt-get -y install libxslt-dev git mosquitto mosquitto-clients libatlas-base-dev python3-scipy python3-paho-mqtt python3-pip python3-flask

# Set hostname to hangboard
#echo raspi-hangboard > /etc/hostname
#FIXME

# Enable MQTT
sudo systemctl start mosquitto    
sudo systemctl enable mosquitto   # autostart (default: on)

# Install python dependencies
python3 -m pip install -r ~/hangboard/backend/requirements.txt
python3 -m pip install -r ~/hangboard/boards/requirements.txt

echo "Install the backend services (manually)"
# FIXME: Automate installation