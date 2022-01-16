run:
	flask run

api-doc:
	docker run -it --rm -v $(PWD):/data ghcr.io/redocly/redoc/cli:v2.0.0-rc.59  bundle ./boards_api.yaml
	mv redoc-static.html api/index.html
	
requirements:
	pip3 install -r requirements.txt

install:
	service="hangboard_assets_delivery.service"
	echo "Install hangboard service for: hangboard_assets_delivery.service" 
	sudo cp ./hangboard_assets_delivery.service /lib/systemd/system/
	sudo chmod 644 /lib/systemd/system/hangboard_assets_delivery.service
	sudo systemctl daemon-reload
	sudo systemctl enable hangboard_assets_delivery.service
	sudo systemctl restart hangboard_assets_delivery.service

