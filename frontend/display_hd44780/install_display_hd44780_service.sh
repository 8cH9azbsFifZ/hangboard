#!/bin/bash
<<<<<<< HEAD:backend/services/install_sensor_force_service.sh
service="sensor_force.service"

echo "Install hangboard service for: "$service 
=======
service="hangboard_display_hd44780.service"

echo "Install hangboard service for: "$service 

>>>>>>> dev:frontend/display_hd44780/install_display_hd44780_service.sh
sudo cp ./$service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/$service
sudo systemctl daemon-reload
sudo systemctl enable $service
sudo systemctl restart $service