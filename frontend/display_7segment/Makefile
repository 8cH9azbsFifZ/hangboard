install:
	service="hangboard_display_7segment.service"
	echo "Install hangboard service for: hangboard_display_7segment.service" 
	sudo cp ./hangboard_display_7segment.service /lib/systemd/system/
	sudo chmod 644 /lib/systemd/system/hangboard_display_7segment.service
	sudo systemctl daemon-reload
	sudo systemctl enable hangboard_display_7segment.service
	sudo systemctl restart hangboard_display_7segment.service

prepare:
	echo "Enable SPI"
	sudo sed -i 's/\#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
	sudo usermod -a -G spi,gpio pi
	sudo apt-get -y install python-dev python-pip libfreetype6-dev libjpeg-dev
	pip3 install luma.led_matrix