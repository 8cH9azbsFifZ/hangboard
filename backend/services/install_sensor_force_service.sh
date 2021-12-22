#!/bin/bash
service="sensor_force.service"
echo "Install service for sensor force" 
sudo cp ./$service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/$service
sudo systemctl daemon-reload
sudo systemctl enable $service
sudo systemctl restart $service