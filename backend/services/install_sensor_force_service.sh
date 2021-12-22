#!/bin/bash
service="sensor_force.service"
<<<<<<< HEAD
echo "Install service for sensor force" 
=======

echo "Install hangboard service for: "$service 

sudo pip3 install scipy # FIXME

>>>>>>> 1244b92b0ceb64cb5e39fa1a57c7c92d8a39f923
sudo cp ./$service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/$service
sudo systemctl daemon-reload
sudo systemctl enable $service
sudo systemctl restart $service