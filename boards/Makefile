run:
	flask run

api-doc:
	echo "#FIXME"

build-images:
	python3 ./generate_all_board_images.py
    # FIXME: all holds images must be genearted and put into assets directory of flutter app.. #83
	rsync -avP --exclude "*.svg" ./cache/. ../frontend/flutter_hangboard/images/.

#install-raspi: -> it is the image creation :(
# illegal instruction	sudo apt-get -y install python3-flask
# docker build does not work on raspi

requirements:
	pip3 install -r requirements.txt

install:
	service="hangboard_board.service"
	echo "Install hangboard service for: hangboard_board.service" 
	sudo cp ./hangboard_board.service /lib/systemd/system/
	sudo chmod 644 /lib/systemd/system/hangboard_board.service
	sudo systemctl daemon-reload
	sudo systemctl enable hangboard_board.service
	sudo systemctl restart hangboard_board.service

