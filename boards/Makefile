run:
	flask run

api-doc:
	echo "#FIXME"

build:
	python3 ./board.py
	echo Later: docker build . -t boards

install-raspi:
	sudo apt-get -y install python3-flask

install:
	service="hangboard_board.service"
	echo "Install hangboard service for: hangboard_board.service" 
	sudo cp ./hangboard_board.service /lib/systemd/system/
	sudo chmod 644 /lib/systemd/system/hangboard_board.service
	sudo systemctl daemon-reload
	sudo systemctl enable hangboard_board.service
	sudo systemctl restart hangboard_board.service

