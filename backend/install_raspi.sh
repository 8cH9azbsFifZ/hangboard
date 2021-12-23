#!/bin/bash

# Prepare for installation
sudo apt-get -y install git

# Download the software
test -e hangboard ||git clone https://github.com/8cH9azbsFifZ/hangboard.git
cd hangboard
git pull

./backend/install_01_prepare_raspi.sh


# Install the python libraries
cd backend
python3 -m pip install -r backend/requirements.txt


echo "Install the backend services (manually)"
# FIXME: Automate installation