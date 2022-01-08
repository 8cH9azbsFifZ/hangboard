install:
	service="hangboard_display_7segment.service"
	echo "Install hangboard service for: hangboard_display_7segment.service" 
	sudo cp ./hangboard_display_7segment.service /lib/systemd/system/
	sudo chmod 644 /lib/systemd/system/hangboard_display_7segment.service
	sudo systemctl daemon-reload
	sudo systemctl enable hangboard_display_7segment.service
	sudo systemctl restart hangboard_display_7segment.service
