#!/bin/bash

# Prepare for installation
sudo apt-get -y install libxslt-dev git

# Download the software
test -e hangboard ||git clone https://github.com/8cH9azbsFifZ/hangboard.git
cd hangboard
git pull

# Install the python libraries
cd backend
python3 -m pip install -r backend/requirements.txt

# Set hostname to hangboard
# FIXME
# set to raspi-hangboard

# Install MQTT
sudo apt-get -y install mosquitto
sudo apt-get -y install mosquitto-clients

#sudo systemctl start mosquitto    # start service
#sudo systemctl stop mosquitto     # stop service
#sudo systemctl enable mosquitto   # autostart (default: on)

# Install docker
curl -fsSL https://get.docker.com | sh


# Install systemd service
sudo cp backend/hangboard-backend.service /etc/systemd/system/
sudo systemctl start hangboard-backend