#!/bin/bash
service="hangboard_display_hd44780.service"

echo "Install hangboard service for: "$service 

sudo cp ./$service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/$service
sudo systemctl daemon-reload
sudo systemctl enable $service
sudo systemctl restart $service