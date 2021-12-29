#!/bin/bash

# Prepare for installation
sudo apt-get -y install libxslt-dev git

# Set hostname to hangboard
# FIXME
# set to raspi-hangboard

# Install MQTT
sudo apt-get -y install mosquitto
sudo apt-get -y install mosquitto-clients

#sudo systemctl start mosquitto    # start service
#sudo systemctl stop mosquitto     # stop service
#sudo systemctl enable mosquitto   # autostart (default: on)

# Install libs for python
sudo apt-get install libatlas-base-dev
