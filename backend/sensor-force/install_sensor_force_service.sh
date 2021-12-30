#!/bin/bash
service="hangboard_sensor_force.service"

echo "Install hangboard service for: "$service 

sudo pip3 install scipy # FIXME

sudo cp ./$service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/$service
sudo systemctl daemon-reload
sudo systemctl enable $service
sudo systemctl restart $service
