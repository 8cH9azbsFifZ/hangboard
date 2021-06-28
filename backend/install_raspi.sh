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




# Install docker
curl -fsSL https://get.docker.com | sh